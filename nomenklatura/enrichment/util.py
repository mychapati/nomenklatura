from Levenshtein import distance

from loom.model import Context, P

SCORE_CUTOFF = 50


def light_normalize(text):
    text = unicode(text)
    text = text.strip().lower()
    return text


def text_score(match, candidates):
    if isinstance(candidates, basestring):
        candidates = [candidates]
    match_n = light_normalize(match)
    best_score = 0
    for candidate in candidates:
        cand_n = light_normalize(candidate)
        dist = float(distance(match_n, cand_n))
        l = float(max(len(match_n), len(cand_n)))
        score = ((l - dist) / l) * 100
        best_score = max(int(score), best_score)
    return best_score


class Service(object):
    SOURCE_LABEL = None
    SOURCE_URL = None

    def __init__(self, graph):
        self.graph = graph

    def create_context(self, root=None, url=None, score=None):
        ctx = Context.create(self.graph)
        ctx.source_label = self.SOURCE_LABEL
        ctx.source_url = self.SOURCE_URL
        ctx.root = root
        ctx.url = url
        ctx.score = score
        return ctx

    def scored_context(self, node, title, url):
        score = text_score(title, node.label)
        if score < SCORE_CUTOFF:
            return
        ctx = self.create_context(root=node, url=url, score=score)
        if score < 99:
            node.add(P.alias, title, ctx)

        node.add(P.url, url, ctx)
        node.add(P.identity, url, ctx)
        return ctx

    def lookup(self, node):
        pass
        
