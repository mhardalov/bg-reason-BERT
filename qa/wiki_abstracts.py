from polyglot.text import Text
import wikipedia
from itertools import chain
import time


wikipedia.set_lang("bg")

def add_abstracts_to_passages(passages, use_nouns=False, verbose=False):
    abstracts = []
    for passage in passages:
        try:
            abstract = add_wiki_abstracts(passage, use_nouns, verbose)
            abstracts.append(passage + abstract)
            if abstract:
                print(len(abstract))
        except ValueError as _:
            print('Another language found')
    return abstracts
    

def add_wiki_abstracts(passage, use_nouns=False, verbose=False):
    """Adds to the passage (context) the wiki abstracts
    of the entities recognized in the passage.

    passage: this is the context that the was retrieved to be
    most relevant for the question + an option.
    """
    text = Text(passage, hint_language_code='bg')
    text.language = 'bg'
    wiki_abstracts = []
    
    ners = [[' '.join(entity) for entity in sent.entities] for sent in text.sentences]
    nouns = []

    if use_nouns:
        nouns = filter(lambda x: x[1] == u'NOUN', text.pos_tags)
        nouns = map(lambda x: x[0], nouns)
    
    for entity in chain(ners, nouns):
        if entity:
            #TODO: да се взима основната форма на думите.
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
        return wikipedia.summary(entity)
    except wikipedia.exceptions.DisambiguationError as e:
        # Sometimes multiple wiki pages are suggested. Adding all of them!
        return '\n'.join(e.options)
    except wikipedia.exceptions.PageError as e:
        # No page for this entity is found
        return ''
    except ConnectionError:
        time.sleep(5)
