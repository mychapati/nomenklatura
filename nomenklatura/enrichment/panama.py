# Dan's Panama Company Database Scrape
#
from lxml import html
from urlparse import urljoin

import requests

from nomenklatura.schema import types
from nomenklatura.enrichment.util import Spider, ContextException


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

    def lookup_company(self, root, entity):
        for title, url, items in scrape(entity.label, 'search/company',
                                        '/company/', 'persons'):
            try:
                ctx = self.scored_context(root, entity, title, url)
            except ContextException:
                continue

            corp = self.create_entity(ctx, types.Company, label=title,
                                      same_as=entity,
                                      links=url)

            for data in items:
                person = self.create_entity(ctx, types.Person,
                                            label=data.get('label'),
                                            links=data.get('url'))
                self.create_entity(ctx, types.Post,
                                   holder=person,
                                   organization=corp,
                                   role=data.get('role'),
                                   links=(url, data.get('url')))

    def lookup_person(self, root, entity):
        for title, url, items in scrape(entity.label, 'personsearch',
                                        '/person/', 'companies'):
            try:
                ctx = self.scored_context(root, entity, title, url)
            except ContextException:
                continue

            person = self.create_entity(ctx, types.Person, label=title,
                                        same_as=entity,
                                        links=url)

            for data in items:
                corp = self.create_entity(ctx, types.Company,
                                          label=data.get('label'),
                                          links=data.get('url'))
                self.create_entity(ctx, types.Post,
                                   holder=person,
                                   organization=corp,
                                   role=data.get('role'),
                                   links=(url, data.get('url')))

    def lookup(self, root, entity):
        if entity.type == types.Company:
            self.lookup_company(root, entity)
        if entity.type == types.Person:
            self.lookup_person(root, entity)
