import collections
import json
import os
from builtins import str


class ModelSetup:
    def __init__(self, model, index, fields, query_size):
        self.model = model
        self.index = index
        self.fields = fields
        self.query_size = query_size

    def to_dict(self):
        setup = {
            'model': self.model,
            'index': self.index,
            'query_field': self.fields.copy(),
            'query_size': self.query_size
        }

        return setup

    def __str__(self):
        setup = self.to_dict()
        return json.dumps(setup, indent=2)


class GridSearch:

    def __init__(self, model):
        self.indecies = None
        self.query_fields = None
        self.query_sizes = None
        self.model = model

    def _get_iterable(x):
        if isinstance(x, collections.Iterable) and not isinstance(x, str):
            return x
        else:
            return (x,)

    def set_indecies(self, indecies):
        self.indecies = GridSearch._get_iterable(indecies)

        return self

    def set_fields(self, fields):
        self.query_fields = fields

        return self

    def set_query_sizes(self, query_sizes):
        self.query_sizes = GridSearch._get_iterable(query_sizes)

        return self

    def __call__(self, *args, **kwargs):
        for idx in self.indecies:
            for fields in self.query_fields:
                for size in self.query_sizes:
                    setup = ModelSetup(self.model, idx, fields, size)
                    yield setup


def export_predictions(path, setup, preds):
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + '/preds.json', 'w') as o:
        json.dump(preds, o, ensure_ascii=False)

    with open(path + '/setup.json', 'w') as o:
        json.dump(setup.to_dict(), o, ensure_ascii=False, indent=2)
