# OpenCorporates
#
# http://api.opencorporates.com/documentation/API-Reference
#
import logging
from urlparse import urljoin
from itertools import count

import requests

from nomenklatura.core import app
from nomenklatura.enrichment.util import Spider


log = logging.getLogger(__name__)
API_HOST = 'https://api.opencorporates.com/'
CORP_ID = 'https://opencorporates.com/companies/'
API_TOKEN = app.config.get('OPENCORPORATES_TOKEN')


def opencorporates_get(path, query):
    url = path if path.startswith('http:') or path.startswith('https:') else urljoin(API_HOST, path)
    params = {'per_page': 200}
    if API_TOKEN is not None:
        params['api_token'] = 'Y2t6PVBfvoJTxhsI0ZJf'
    params.update(query)
    res = requests.get(url, params=params)
    return res.json()


def opencorporates_paginate(path, collection_name, item_name, query):
    res = {}
    for i in count(1):
        if i > res.get('total_pages', 10000):
            return
        res = opencorporates_get(path, query)
        if 'error' in res:
            return
        res = res.get('results', {})
        for data in res.get(collection_name, []):
            data = data.get(item_name)
            yield data


class OpenCorporatesSpider(Spider):
    PUBLISHER_LABEL = 'OpenCorporates'
    PUBLISHER_URL = 'https://opencorporates.com'

    def make_api_url(self, url):
        if '://api.' not in url:
            url = url.replace('://', '://api.')
        return url

    def expand_company(self, node, url, ctx):
        if ctx is None:
            ctx = self.create_context(root=node, url=url, score=100)

        api_url = self.make_api_url(url)
        data = opencorporates_get(api_url, {})
        data = data.get('results', {}).get('company', {})
        node.add(P.identity, api_url, ctx)
        node.add(P.jurisdiction, data.get('jurisdiction_code'), ctx)
        node.add(P.company_number, data.get('company_number'), ctx)
        node.add(P.company_type, data.get('company_type'), ctx)

        for officer in data.get('officers', []):
            officer = officer.get('officer')
            off_url = officer.get('opencorporates_url')
            off = self.graph.node(context=ctx)
            off.add(P.identity, off_url)
            off.add(P.url, off_url)
            off.add(P.label, officer.get('name'))
            #off.add(P.is_a, T.Company)

            link = self.graph.link(ctx, off, P.officer_of, node)
            link.add(P.identity, off_url + '#rel')
            if officer.get('start_date'):
                link.add(P.start_date, officer.get('start_date'))
            if officer.get('end_date'):
                link.add(P.end_date, officer.get('end_date'))
            link.add(P.position, officer.get('position'))

    def lookup_companies(self, node, label):
        identities = [(s.value, s.context) for s in node.get(P.identity,
                                                             active=False)]
        for identity, ctx in identities:
            if not identity.startswith(CORP_ID):
                continue
            api_url = self.make_api_url(identity)
            if (api_url, ctx) in identities:
                continue
            self.expand_company(node, identity, ctx)

        identities = [url for (url, ctx) in identities]
        query = {'q': label}
        for company in opencorporates_paginate('companies/search', 'companies',
                                               'company', query):
            url = company.get('opencorporates_url')
            ctx = self.scored_context(node, company.get('name'), url)
            if ctx is None:
                break

            self.expand_company(node, url, ctx)

    def lookup_officer(self, node, label):
        query = {'q': label}
        for officer in opencorporates_paginate('officers/search', 'officers',
                                               'officer', query):
            url = officer.get('opencorporates_url')
            ctx = self.scored_context(node, officer.get('name'), url)
            if ctx is None:
                break

            corp_data = officer.get('company')
            corp = self.graph.node(context=ctx)
            corp.add(P.identity, corp_data.get('opencorporates_url'))
            corp.add(P.label, corp_data.get('name'))
            corp.add(P.is_a, T.Company)

            link = self.graph.link(ctx, node, P.officer_of, corp)
            link.add(P.identity, url + '#rel')
            if officer.get('start_date'):
                link.add(P.start_date, officer.get('start_date'))
            if officer.get('end_date'):
                link.add(P.end_date, officer.get('end_date'))
            link.add(P.position, officer.get('position'))

    def lookup(self, node, label):
        if node.is_a(T.Company):
            self.lookup_companies(node, label)
        self.lookup_officer(node, label)
