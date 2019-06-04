import collections
import json
import argparse
import sys
import numpy as np

OPTS = None


def parse_args():
    parser = argparse.ArgumentParser('Official evaluation script for BG_RC version 1.0.')
    parser.add_argument('data_file', metavar='data.json', help='Input data JSON file.')
    parser.add_argument('pred_file', metavar='pred.json', help='Model predictions.')
    parser.add_argument('--out-file', '-o', metavar='eval.json',
                        help='Write accuracy metrics to file (default is stdout).')
    parser.add_argument('--verbose', '-v', action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def flatten_dataset(dataset):
    ds = {}
    for (category, items) in dataset.items():
        for questions in items:
            for q in questions['questions']:
                ds[q['id']] = {'answer': q['correct'], 'url': questions['url'], 'category': category}

    return ds


def merge_eval(main_eval, new_eval, prefix):
    for k in new_eval:
        main_eval['%s_%s' % (prefix, k)] = new_eval[k]


def make_eval_dict(accuracy_scores):
    correct, total = accuracy_scores

    return collections.OrderedDict([('total', total),
                                    ('accuracy', 100.0 * correct / total)])


def get_raw_evaluation(qa_ds, preds):
    totals = np.zeros(2, dtype=np.int32)
    accuracy_scores = {}

    for (qid, pred) in preds.items():
        if qid not in qa_ds:
            continue

        question = qa_ds[qid]
        category = question['category']

        if category not in accuracy_scores:
            accuracy_scores[category] = [0, 0]

        cat_acc = accuracy_scores[category]

        is_correct = int(pred == question['answer'])
        cat_acc[0] += is_correct
        cat_acc[1] += 1

        totals += [int(pred == question['answer']), 1]

    return accuracy_scores, totals.tolist()


def main():
    with open(OPTS.data_file) as f:
        dataset_json = json.load(f)
        dataset = dataset_json['data']
    with open(OPTS.pred_file) as f:
        preds = json.load(f)

    qa_flatten = flatten_dataset(dataset)

    accuracy_scores, totals = get_raw_evaluation(qa_flatten, preds)

    out_eval = make_eval_dict(totals)

    for (cat, acc) in accuracy_scores.items():
        eval_dict = make_eval_dict(acc)
        merge_eval(out_eval, eval_dict, cat)

    if OPTS.out_file:
        with open(OPTS.out_file, 'w') as f:
            json.dump(out_eval, f, indent=2)
    else:
        print(json.dumps(out_eval, indent=2))


if __name__ == '__main__':
    OPTS = parse_args()
    # if OPTS.out_image_dir:
    # import matplotlib

    # matplotlib.use('Agg')
    # import matplotlib.pyplot as plt

    main()
