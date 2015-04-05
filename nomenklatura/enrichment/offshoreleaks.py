# OffshoreLeaks (http://www.icij.org/offshore)
#
from urlparse import urljoin

from lxml import html
import requests

from nomenklatura.schema import types
from nomenklatura.enrichment.util import Spider, ContextException

QUERY_URL = 'http://offshoreleaks.icij.org/search'

TYPES = {
    'officer': types.Person,
    'company': types.Company,
    'entity': types.Company
}


def scrape(label, fld, cls):
    res = requests.get(QUERY_URL, params={
        'q': label,
        'country': '',
        fld: 'on'
    })
    doc = html.fromstring(res.content)
    for ent in doc.findall('.//li[@class="%s"]' % cls)[:10]:
        link = ent.find('./a')
        if link is None:
            continue
        href = urljoin(QUERY_URL, link.get('href'))
        res = requests.get(href, headers={'Accept': 'application/json'})
        res = res.json()
        res['id'] = res.get('node').get('id')
        res['url'] = 'http://offshoreleaks.icij.org/nodes/%s' % res['id']
        yield res


class OffshoreLeaksSpider(Spider):
    PUBLISHER_LABEL = 'ICIJ OffshoreLeaks'
    PUBLISHER_URL = 'http://offshoreleaks.icij.org'

    def parse_graph(self, data):
        root_id = data.get('node', {}).get('id')
        graph = data.get('graph', {})
        for node in graph.get('nodes'):
            node_id = node.get('id')
            if node_id == root_id:
                continue
            if node.get('subtype') not in TYPES:
                continue
            for edge in graph.get('edges'):
                if edge.get('source') == node_id or \
                        edge.get('target') == node_id:
                    yield node, edge

    def lookup_company(self, root, entity):
        for data in scrape(entity.label, 'ent', 'results-type-entity'):
            try:
                ctx = self.scored_context(root, entity, data.get('title'),
                                          data.get('url'))
            except ContextException:
                continue

            corp = self.create_entity(ctx, types.Company,
                                      label=data.get('title'),
                                      same_as=entity,
                                      links=data.get('url'))
            # TODO: reconcile: data.get('node').get('taxJurisdiction')

            for n, e in self.parse_graph(data):
                url = urljoin(data.get('url'), str(n.get('id')))
                off = self.create_entity(ctx, TYPES.get(n.get('subtype')),
                                         label=n.get('label'),
                                         links=url)
                self.create_entity(ctx, types.Post,
                                   holder=off,
                                   organization=corp,
                                   role=e.get('label'),
                                   links=(url, data.get('url')))

    def lookup_officer(self, root, entity):
        for data in scrape(entity.label, 'ppl', 'results-type-officer'):
            try:
                ctx = self.scored_context(root, entity, data.get('title'),
                                          data.get('url'))
            except ContextException:
                continue

            off = self.create_entity(ctx, types.Actor,
                                     label=data.get('title'),
                                     same_as=entity,
                                     links=data.get('url'))

            for n, e in self.parse_graph(data):
                url = urljoin(data.get('url'), str(n.get('id')))
                corp = self.create_entity(ctx, TYPES.get(n.get('subtype')),
                                          label=n.get('label'),
                                          links=url)
                self.create_entity(ctx, types.Post,
                                   holder=off,
                                   organization=corp,
                                   role=e.get('label'),
                                   links=(url, data.get('url')))

    def lookup(self, root, entity):
        if types.Company.matches(entity.type):
            self.lookup_company(root, entity)
        self.lookup_officer(root, entity)
