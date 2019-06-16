from polyglot.text import Text
import wikipedia
from itertools import chain
import time


wikipedia.set_lang("bg")

def get_wiki_abstracts(sentences, verbose=False):
    abstracts = []
    for sentence in sentences:
        try:
            abstracts.append(add_wiki_abstracts(sentence, verbose))
            if abstracts[-1]:
                print("abstract's length is %d " % len(abstracts[-1]))
                print(abstracts[-1])
        except ValueError as _:
            print('Another language found')
    return abstracts


def get_entities(sentence):
    text = Text(sentence, hint_language_code='bg')
    ners = [[' '.join(entity) for entity in sent.entities] for sent in text.sentences]
    if [] in ners:
        ners.remove([])
    nouns = map(lambda x: x[0], filter(lambda x: x[1] == 'NOUN', text.pos_tags))
    
    return chain(ners, nouns)


def add_wiki_abstracts(sentence, verbose):
    """Adds to the sentence (context) the wiki abstracts
    of the entities recognized in the sentence.

    sentence: this is the context that the was retrieved to be
    most relevant for the question + an option.
    """
    wiki_abstracts = []
    for entity in get_entities(sentence):
        if entity:
            print("Entity found %s" % entity)
            wiki_abstracts.append(find_wiki_abstract(entity))
    
    abstract = '\n'.join(wiki_abstracts)
    if verbose:
        print('wiki: %s' % abstract)
    return abstract

def find_wiki_abstract(entity):
    """Finds the wiki abstract(s) for an entity """

    # TODO: use wikipedia.suggest - wikipedia.suggest returns the suggested
    # Wikipedia title for a query, or None. For some reason, it's always None.
    try:
        return wikipedia.summary(entity, chars=200, auto_suggest=True)
    except wikipedia.exceptions.DisambiguationError as e:
        # Sometimes multiple wiki pages are suggested. Adding all of them!
        return '\n'.join(e.options)
    except wikipedia.exceptions.PageError as e:
        # No page for this entity is found
        return ''
    except ConnectionError:
        time.sleep(5)
        return ''
