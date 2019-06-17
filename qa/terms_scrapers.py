import pickle
from lxml import html
import requests
from googletrans import Translator
import wikipedia
import json


TARGET_LANGUAGE = 'bg'
WIKI_GLOSSARIES = [
    'Glossary_of_biology',
    'Glossary_of_geography_terms',
    'Glossary_of_philosophy',
    'Glossary_of_history',
]

def scrape_ecodb_bas():
    page_url = 'http://e-ecodb.bas.bg/rdb/bg/vol3/08dict.html'
    page = requests.get(page_url)
    tree = html.fromstring(page.content)
    terms_names = tree.xpath('//dt/text()')
    terms_definitions = list(map(lambda x: x.text_content(), tree.xpath('//dd')))
    return dict(zip(terms_names, terms_definitions))



def scrape_wiki_glossary(wiki_glossary):
    tree = html.fromstring(wikipedia.page(wiki_glossary).html())
    terms = tree.xpath('//dl[@class="glossary"]/*')
    terms = list(filter(lambda e: e.tag in ['dt', 'dd'], terms))
    terms_dict = {}
    while terms:
        term_name = terms.pop(0).text_content()
        if terms[0].tag == 'dd':
            term_def = terms.pop(0).text_content()
        else:
            term_def = ''
        terms_dict.update({term_name: term_def})
    return terms_dict
    #terms_definitions = list(map(lambda x: x.text_content(), tree.xpath('//dd[@class="glossary"]')))
    #return dict(zip(terms_names, terms_definitions))

def scrape_and_translate_wiki_glossaries():
    all_terms = {}
    for wiki_glossary in WIKI_GLOSSARIES:
        all_terms.update(scrape_wiki_glossary(wiki_glossary))
        print('Scraped %s' % wiki_glossary)
    print(len(all_terms))
    translated_terms = {}

    i = 0
    for term, definition in all_terms.items():
        translator = Translator()
        print(term)
        term_bg = translator.translate(term, TARGET_LANGUAGE).text
        print(term_bg)
        definition_bg = translator.translate(definition, TARGET_LANGUAGE).text
        translated_terms[term_bg] = definition_bg
        i += 1
        if i % 20 == 0:
            print(i)
    return translated_terms


with open('ecodb.json', 'w', encoding='utf8') as fp:
    json.dump(scrape_ecodb_bas(), fp, sort_keys=True, indent=4, ensure_ascii=False)

#def save_obj(obj, name):
#    with open('obj/'+ name + '.pkl', 'wb') as f:
#        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# save_obj(scrape_and_translate_wiki_glossaries(), 'wiki_glossaries')
with open('wiki2.json', 'w', encoding='utf8') as fp:
    json.dump(scrape_and_translate_wiki_glossaries(), fp, sort_keys=True, indent=4, ensure_ascii=False)
