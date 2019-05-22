import numpy as np
import torch
import argparse

from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForQuestionAnswering
from tqdm import tqdm

from elasticsearch import Elasticsearch

from dataset.bgquiz import BGQuiz
from qa.utils import qa
from search.commons import ElasticConfig
from collections import Counter

query_field = [
    'title.bulgarian', 'passage.ngram',
    'passage', 'passage.bulgarian^2'
]


def main():
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument("--es_config_file",
                        default=None,
                        type=str,
                        required=True,
                        help="The config json file corresponding to ElasticSearch instance.")

    parser.add_argument("--pytorch_bert_path",
                        default=None,
                        type=str,
                        required=True,
                        help="Path to the pre-trained PyTorch model.")

    parser.add_argument('--quizes', nargs='+', help='List of Quiz json files', required=True)

    # Optional parameters
    parser.add_argument('--use_gpu', default=False, action='store_true',
                        help='Whether to use GPU or not')
    args = parser.parse_args()

    quiz = BGQuiz(args.quizes).json_data

    bert_path = args.pytorch_bert_path
    # BertForQA model with GPU support
    model = BertForQuestionAnswering.from_pretrained(bert_path)
    # Add specific options if needed
    tokenizer = BertTokenizer.from_pretrained(bert_path, do_lower_case=False)

    if args.use_gpu:
        model.to('cuda')

    es_conf = ElasticConfig(args.es_config_file)
    es = Elasticsearch(es_conf.host, port=es_conf.port)

    cnt = 0
    t = 0
    for i, row in enumerate(quiz):
        try:
            question = row['question'].replace(":", '?')
            #         wiki = row['info']
            correct = row['correct']
            answers = row['answers']

            print("{}/{}".format(i, len(quiz)), question, row['correct'])
            print(answers)

            pred = qa(es, 'bgwiki_paragraph', model, tokenizer, question, num_hits=10, query_field=query_field,
                      use_gpu=args.use_gpu)
            c = Counter()
            for r in pred:
                c[r[0]] += 1
                print(r)

            #         answer = c.most_common()[0][0] if len(c) > 0 else ''
            answer = ''

            for (ans, _) in c.most_common():
                for cans in answers:
                    if (cans == ans or cans.lower() in ans.lower() or
                            ans.lower() in cans.lower()):
                        answer = cans
                        break

                if len(answer):
                    break

            if len(answer) == 0:
                answer = '[CLS]'

            #         if correct.lower() not in wiki.lower():
            # #             print(wiki)
            #             print(question)
            #             print(correct)
            # #             print()
            #         else: continue

            #         answer = predict(model, tokenizer, question, wiki)[0]

            corr = (answer != '' and (correct == answer or correct.lower() in answer.lower() or
                                      answer.lower() in correct.lower()))

            print(answer, corr)
            print()
            t += 1
            if corr:
                cnt += 1
            #             continue
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            print()

    print(cnt, t)


if __name__ == "__main__":
    main()
