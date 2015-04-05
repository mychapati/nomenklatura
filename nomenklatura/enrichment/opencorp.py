# OpenCorporates
#
# http://api.opencorporates.com/documentation/API-Reference
#
import logging
from urlparse import urljoin
from itertools import count

import requests

from nomenklatura.core import app
from nomenklatura.schema import types
from nomenklatura.enrichment.util import Spider, ContextException


log = logging.getLogger(__name__)
API_HOST = 'https://api.opencorporates.com/'
CORP_ID = 'https://opencorporates.com/companies/'
API_TOKEN = app.config.get('OPENCORPORATES_TOKEN')


def opencorporates_get(path, query):
    url = path if path.startswith('http:') or path.startswith('https:') \
        else urljoin(API_HOST, path)
    params = {'per_page': 200}
    if API_TOKEN is None:
        log.warning("No OpenCorporates API key configured!")
    else:
        params['api_token'] = API_TOKEN
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

    def expand_company(self, entity, ctx, url, skip_officer=None):
        api_url = self.make_api_url(url)
        data = opencorporates_get(api_url, {})
        data = data.get('results', {}).get('company', {})

        country = self.get_country(iso2=data.get('jurisdiction_code'))
        if country is not None:
            entity.set(types.Company.attributes.jurisdiction,
                       country, ctx)
        entity.set(types.Company.attributes.opencorporates_url,
                   url, ctx)
        entity.set(types.Company.attributes.company_number,
                   data.get('company_number'), ctx)
        entity.set(types.Company.attributes.company_type,
                   data.get('company_type'), ctx)
        entity.set(types.Company.attributes.current_status,
                   data.get('current_status'), ctx)

        for officer in data.get('officers', []):
            officer = officer.get('officer')
            off_url = officer.get('opencorporates_url')

            if skip_officer is not None and officer.get('name') == skip_officer:
                continue

            off = self.create_entity(ctx, types.Actor,
                                     label=officer.get('name'),
                                     links=url)

            post = self.create_entity(ctx, types.Post,
                                      holder=off,
                                      organization=entity,
                                      role=officer.get('position'),
                                      links=off_url)

            if officer.get('start_date'):
                post.set(types.Company.attribute.start_date,
                         officer.get('start_date'), ctx)
            if officer.get('end_date'):
                post.set(types.Company.attribute.start_date,
                         officer.get('start_date'), ctx)

    def lookup_companies(self, root, entity):
        url = entity.get(types.Company.attributes.opencorporates_url)
        if url:
            try:
                ctx = self.scored_context(root, entity, entity.label, url)
                self.expand_company(entity, ctx, url)
            except ContextException:
                pass
            return

        query = {'q': entity.label}
        for company in opencorporates_paginate('companies/search', 'companies',
                                               'company', query):
            url = company.get('opencorporates_url')
            try:
                ctx = self.scored_context(root, entity, company.get('name'),
                                          url)
            except ContextException:
                continue

            corp = self.create_entity(ctx, types.Company,
                                      label=company.get('name'),
                                      same_as=entity,
                                      opencorporates_url=url)
            self.expand_company(corp, ctx, url)

    def lookup_officer(self, root, entity):
        query = {'q': entity.label}
        for officer in opencorporates_paginate('officers/search', 'officers',
                                               'officer', query):
            url = officer.get('opencorporates_url')
            try:
                ctx = self.scored_context(root, entity, officer.get('name'),
                                          url)
            except ContextException:
                continue

            off = self.create_entity(ctx, types.Actor,
                                     label=officer.get('name'),
                                     same_as=entity,
                                     links=url)

            corp_data = officer.get('company')
            corp_url = corp_data.get('opencorporates_url')
            corp = self.create_entity(ctx, types.Company,
                                      label=corp_data.get('name'),
                                      opencorporates_url=corp_url)

            post = self.create_entity(ctx, types.Post,
                                      holder=off,
                                      organization=corp,
                                      role=officer.get('position'),
                                      links=url)

            if officer.get('start_date'):
                post.set(types.Company.attribute.start_date,
                         officer.get('start_date'), ctx)
            if officer.get('end_date'):
                post.set(types.Company.attribute.start_date,
                         officer.get('start_date'), ctx)

            self.expand_company(corp, ctx, corp_url,
                                skip_officer=officer.get('name'))

    def lookup(self, root, entity):
        if types.Company.matches(entity.type):
            self.lookup_companies(root, entity)
        self.lookup_officer(root, entity)
