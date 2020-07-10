from urllib.parse import quote as url_encode

from . import caniuse
from .caniuse import Browser, support_for_feature

CHARS = {'y': '✔', 'n': '✘', 'a': '◒', 'u': '‽', 'i': 'ⓘ', 'w': '!'}

QUERY_BROWSERS = [
    Browser.EDGE, Browser.CHROME, Browser.FIREFOX, Browser.SAFARI
]

BROWSERS = {
    'edge': 'Edge',
    'chrome': 'Chr',
    'firefox': 'FF',
    'safari': 'Safari'
}


def make_tweet(feats, query, max_feats):
    lines = []

    for feat in feats[:max_feats]:
        lines.append(feat['title'])
        for browser in QUERY_BROWSERS:
            line = f"{BROWSERS[browser.value]} "
            supports = support_for_feature(feat, browser)[:2][::-1]
            support_txts = []
            for support in supports:
                support_txts.append(
                    f"{CHARS[support['status']]} {support['version']}+")
            line += ' '.join(support_txts)
            lines.append(line)
        lines.append("")

    url = f"https://caniuse.com/#search={url_encode(query)}"

    if len(feats) > max_feats:
        lines.append(f"+{len(feats) - max_feats} {url}")
    else:
        lines.append(url)

    tweet = '\n'.join(lines)
    return tweet


def generate_tweet(query: str) -> str:
    cani = caniuse.CanIUseDB()

    feats = cani.get_features(query)

    if feats is None:
        return f"Couldn't find anything for {query[:252]}."

    if type(feats) is dict:
        feats = [feats]

    tweet = None
    for i in range(3, 0, -1):
        _tweet = make_tweet(feats, query, i)
        if len(_tweet) <= 280:
            tweet = _tweet
            break

    if tweet is None:
        tweet = f"{len(feats)} results at https://caniuse.com/#search={url_encode(query)}"

    return tweet
