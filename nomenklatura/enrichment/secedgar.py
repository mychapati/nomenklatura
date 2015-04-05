from urlparse import urljoin

import requests
from lxml import html

from nomenklatura.schema import types
from nomenklatura.enrichment.util import Spider, ContextException

CIK_URL = 'http://www.sec.gov/cgi-bin/cik.pl.c'


class SecEdgarSpider(Spider):
    PUBLISHER_LABEL = 'US Securities and Exchange Commission'
    PUBLISHER_URL = 'http://www.sec.gov/'

    def lookup(self, root, entity):
        if types.Company.matches(entity.type):
            return

        q = {'company': entity.label}
        res = requests.post(CIK_URL, data=q)
        doc = html.fromstring(res.content)
        for link in doc.findall('.//pre/a'):
            href = urljoin(CIK_URL, link.get('href'))
            title = link.tail.strip()

            try:
                ctx = self.scored_context(root, entity, title, href)
                self.create_entity(ctx, types.Company,
                                   label=title,
                                   links=href,
                                   same_as=entity,
                                   cik=link.text)
            except ContextException:
                continue
