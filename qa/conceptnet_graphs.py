import requests
#from google.cloud import translate
from googletrans import Translator
from nltk.tokenize import word_tokenize, sent_tokenize, wordpunct_tokenize
from itertools import chain
from nltk.corpus import wordnet as wn
from polyglot.text import Text
# from qa.wiki_abstracts import get_entities


def get_entities(sentence):
    text = Text(sentence, hint_language_code='bg')
    ners = [[' '.join(entity) for entity in sent.entities] for sent in text.sentences]
    ners.remove([])
    nouns = map(lambda x: x[0], filter(lambda x: x[1] == 'NOUN', text.pos_tags))
    
    return chain(ners, nouns)


"""
There are three methods for accessing data through the ConceptNet 5 API: lookup, search, and association.

  - Lookup is for when you know the URI of an object in ConceptNet, and want to see a list of edges that include it.
  - Search finds a list of edges that match certain criteria.
  - Association is for finding concepts similar to a particular concept or a list of concepts.
"""
TARGET_LANGUAGE = 'bg'
TARGET_LANGUAGE_f = 'bul'
CONCEPT_NET_URL = 'http://api.conceptnet.io/'
NODE_URL = 'http://api.conceptnet.io/c/bg/{}?filter=/c/bg&limit=3'
# Using the English relations because there is more information
# and then translating them back to Bulgarian.
RELATED_NODES_URL = 'http://api.conceptnet.io/related/c/bg/{}?filter=/c/en&limit=4'
# translate_client = translate.Client()
translator = Translator()

def get_base_form(entity):
  obj = requests.get(NODE_URL.format(entity)).json()
  if not obj['edges']:
    return None
  return obj['edges'][0]['end']['label']


def get_related_entities(entity): 
  related = requests.get(RELATED_NODES_URL.format(get_base_form)).json()['related']
  related = map(lambda x: ' '.join(x["@id"].split('/')[-1].split('_')), related)

  #translations = translate_client.translate(
  #  ' '.join(related),
  #  target_language=TARGET_LANGUAGE)['translatedText']

  translated = set(translator.translate(' '.join(related), TARGET_LANGUAGE).text.split(' '))
  return translated


def get_synonyms(entity):
  synonyms = wn.lemmas(entity, lang='bul')
  if not synonyms:
    return set()
  synonyms = wn.lemmas(entity, lang='bul')[0].synset().lemmas(lang='bul')
  return set([s.name() for s in synonyms])


def enrich_sentence(sentence):
  entities = [get_base_form(entity) for entity in get_entities(sentence)]
  entities = [e for e in entities if e]
  additions = []
  for entity in entities:
    additions.extend(get_synonyms(entity) | get_related_entities(entity))

  return ' '.join(additions)
