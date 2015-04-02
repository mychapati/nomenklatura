from normality import normalize
from Levenshtein import jaro_winkler

from nomenklatura.core import db
from nomenklatura.model import Context

SCORE_CUTOFF = 50


def text_score(match, candidates):
    if isinstance(candidates, basestring):
        candidates = [candidates]
    match_n = normalize(match)
    best_score = 0
    for candidate in candidates:
        cand_n = normalize(candidate)
        score = jaro_winkler(match_n, cand_n, 0.02) * 100
        best_score = max(int(score), best_score)
    return best_score


class LowScoreException(Exception):
    pass


class Spider(object):
    PUBLISHER_LABEL = None
    PUBLISHER_URL = None

    def create_context(self, root=None, url=None, score=None):
        ctx = Context.create(None, {
            'active': False,
            'source_url': url,
            'publisher': self.PUBLISHER_LABEL,
            'publisher_url': self.PUBLISHER_URL
        })
        # ctx.enrich_root = root
        ctx.score = score
        db.session.add(ctx)
        return ctx

    def scored_context(self, entity, title, url):
        score = text_score(title, entity.label)
        if score < SCORE_CUTOFF:
            return
        return self.create_context(root=entity.id, url=url,
                                   score=score)

    def lookup(self, entity):
        pass
