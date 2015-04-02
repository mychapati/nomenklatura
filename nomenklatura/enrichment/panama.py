# Dan's Panama Company Database Scrape
#
from lxml import html
from urlparse import urljoin
from urllib import quote

import requests

from nomenklatura.schema import types, attributes
from nomenklatura.enrichment.util import Spider, LowScoreException


HOST_URL = 'http://ohuiginn.net/panama/'


def scrape(label, path, filter, field):
    url = urljoin(HOST_URL, path)
    res = requests.get(url, params={'name': label})
    doc = html.fromstring(res.content)
    for link in doc.findall('.//a'):
        href = urljoin(HOST_URL, link.get('href'))
        if filter not in href:
            continue
        pres = requests.get(href)
        pdoc = html.fromstring(pres.content)
        items = []
        role = None
        for item in pdoc.findall("./*"):
            if item.tag == 'h2':
                role = item.text
            elif item.tag == 'ul':
                for a in item.findall('.//a'):
                    items.append({
                        'role': role,
                        'label': a.text,
                        'url': urljoin(HOST_URL, a.get('href'))
                    })
        yield pdoc.findtext('./h1'), href, items


class PanamaSpider(Spider):
    PUBLISHER_LABEL = 'Panama Companies'
    PUBLISHER_URL = 'http://ohuiginn.net/panama/'

    def lookup_company(self, entity):
        for title, url, items in scrape(entity.label, 'search/company',
                                        '/company/', 'persons'):
            try:
                ctx = self.scored_context(entity, title, url)
            except LowScoreException:
                continue

            for data in items:
                off = self.graph.node(context=ctx)
                off.add(P.label, data.get('label'))
                off.add(P.is_a, T.Person)
                off.add(P.url, data.get('url'))
                off.add(P.identity, data.get('url'))

                link = self.graph.link(ctx, off, P.officer_of, node)
                link.add(P.identity, url + '#' + quote(data.get('label')))
                link.add(P.position, data.get('role'))

    def lookup_person(self, entity):
        for title, url, items in scrape(entity.label, 'personsearch',
                                        '/person/', 'companies'):
            try:
                ctx = self.scored_context(entity, title, url)
            except LowScoreException:
                continue

            for data in items:
                corp = self.graph.node(context=ctx)
                corp.add(P.label, data.get('label'))
                corp.add(P.is_a, T.Company)
                corp.add(P.url, data.get('url'))
                corp.add(P.identity, data.get('url'))

                link = self.graph.link(ctx, node, P.officer_of, corp)
                link.add(P.identity, data.get('url') + '#' + quote(title))
                link.add(P.position, data.get('role'))

    def lookup(self, entity):
        if entity.type == types.Company:
            self.lookup_company(entity)
        if entity.type == types.Person:
            self.lookup_person(entity)
