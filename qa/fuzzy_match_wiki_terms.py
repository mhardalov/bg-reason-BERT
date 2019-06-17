import json
from fuzzywuzzy import fuzz

RATIO = 70

with open('qa/wiki.json') as f:
    wiki_glossary_terms = json.load(f)

wiki_keys = list(wiki_glossary_terms)


def fuzzy_match_terms(sentence):
    print('Searching in %s' % sentence)
    add_info = []
    for k, v in wiki_glossary_terms.items():
        ratio = fuzz.token_set_ratio(k, sentence)
        if ratio > RATIO:
            print('Found %s with ratio %d' % (k, ratio))
            add_info.append(v)
    
    return ' '.join(add_info)
