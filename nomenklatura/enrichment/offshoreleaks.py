# OffshoreLeaks (http://www.icij.org/offshore)
#
from lxml import html
from urlparse import urljoin
from urllib import quote
import requests

from nomenklatura.enrichment.util import Service

QUERY_URL = 'http://offshoreleaks.icij.org/search'

TYPES = {
    'officer': T.Person,
    'company': T.Company,
    'entity': T.Company
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


class OffshoreLeaksService(Service):
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

    def lookup_company(self, node, label):
        for data in scrape(label, 'ent', 'results-type-entity'):
            ctx = self.scored_context(node, data.get('title'), data.get('url'))
            if ctx is None:
                continue

            if data.get('node').get('taxJurisdiction'):
                node.add(P.jurisdiction, data.get('jurisdiction'), ctx)

            for n, e in self.parse_graph(data):
                off = self.graph.node(context=ctx)
                off.add(P.label, n.get('label'))
                off.add(P.is_a, TYPES.get(n.get('subtype')))
                url = urljoin(data.get('url'), str(n.get('id')))
                off.add(P.url, url)
                off.add(P.identity, url)
                link = self.graph.link(ctx, off, P.officer_of, node)
                lurl = url + '#' + quote(str(data.get('id')))
                link.add(P.identity, lurl)
                link.add(P.position, e.get('label'))

    def lookup_officer(self, node, label):
        for data in scrape(label, 'ppl', 'results-type-officer'):
            ctx = self.scored_context(node, data.get('title'), data.get('url'))
            if ctx is None:
                continue

            for n, e in self.parse_graph(data):
                corp = self.graph.node(context=ctx)
                corp.add(P.label, n.get('label'))
                corp.add(P.is_a, TYPES.get(n.get('subtype')))
                url = urljoin(data.get('url'), str(n.get('id')))
                corp.add(P.url, url)
                corp.add(P.identity, url)
                link = self.graph.link(ctx, node, P.officer_of, corp)
                lurl = data.get('url') + '#' + quote(str(n.get('id')))
                link.add(P.identity, lurl)
                link.add(P.position, e.get('label'))

    def lookup(self, node, label):
        if node.is_a(T.Company):
            self.lookup_company(node, label)
        self.lookup_officer(node, label)
