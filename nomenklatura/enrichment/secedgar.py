from urlparse import urljoin

import requests
from lxml import html

from nomenklatura.enrichment.util import Spider

CIK_URL = 'http://www.sec.gov/cgi-bin/cik.pl.c'


class SecEdgarSpider(Spider):
    PUBLISHER_LABEL = 'US Securities and Exchange Commission'
    PUBLISHER_URL = 'http://www.sec.gov/cgi-bin/cik.pl.c'

    def lookup(self, node, label):
        if not node.is_a(T.Company):
            return

        q = {'company': label}
        res = requests.post(CIK_URL, data=q)
        doc = html.fromstring(res.content)
        for link in doc.findall('.//pre/a'):
            href = urljoin(CIK_URL, link.get('href'))
            title = link.tail.strip()

            ctx = self.scored_context(node, title, href)
            node.add(P.company_number, link.text, ctx)
