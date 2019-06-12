import json
import argparse
import os

from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from search.commons import ElasticConfig


def create_doc(title, isbn, passage, page):
    doc = {'title': title,
           'isbn': isbn,
           'passage': passage,
           'page': page,
           'timestamp': datetime.now()}

    return doc


def create_index(es, es_conf):
    _ = es.indices.delete(index=es_conf.index_name, ignore=[400, 404])
    es.indices.create(index=es_conf.index_name, ignore=400, body=es_conf.schema)


def fill_index(es, es_conf, root):
    actions = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            with open(os.path.join(path, name), 'r') as f:
                print(f.name)
                line = f.readline()
                while line:
                    article = json.loads(line)
                    line = f.readline()

                    if es_conf.use_paragraphs:
                        if es_conf.window > 0:
                            paragraphs = [
                                article['text'][i:(i + es_conf.window)]
                                for i in range(0, len(article['text']), es_conf.stride)
                            ]
                        else:
                            paragraphs = [
                                x.strip() for x in
                                article['text'].split("\n")
                                if len(x.strip())
                            ]
                    else:
                        paragraphs = [article['text']]

                    for paragraph in paragraphs:
                        doc = create_doc(article['title'], article['url'],
                                         paragraph, int(article['id']))
                        # res = es.index(index="test-index", doc_type='tweet', id=id, body=doc)

                        action = {
                            "_index": es_conf.index_name,
                            #                         "_type": "passage",
                            #                         "_id": doc["page"],
                            "_source": doc
                        }
                        actions.append(action)
                        if len(actions) == es_conf.batch_size:
                            print("Pushed {} rows".format(len(actions)))
                            helpers.bulk(es, actions, request_timeout=60)
                            del actions[:]

    if len(actions) > 0:
        helpers.bulk(es, actions)
        print("Pushed {} rows".format(len(actions)))


def main():
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument("--wiki_path",
                        default=None,
                        type=str,
                        required=True,
                        help="Path to the documents.")
    parser.add_argument("--es_config_file",
                        default=None,
                        type=str,
                        required=True,
                        help="The config json file corresponding to ElasticSearch instance.")

    args = parser.parse_args()

    es_conf = ElasticConfig(args.es_config_file)
    es = Elasticsearch(es_conf.host, port=es_conf.port)

    create_index(es, es_conf)
    fill_index(es, es_conf, args.wiki_path)


if __name__ == "__main__":
    main()
