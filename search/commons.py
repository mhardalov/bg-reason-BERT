import json


class ElasticConfig(object):

    def __init__(self, path):
        with open(path, "r") as f:
            conf = json.load(f)
            self.host = conf["host"]
            self.port = conf["port"]
            self.index_name = conf["index_name"]
            self.schema = conf["es_schema"]
            self.batch_size = conf["batch_size"]
            self.use_paragraphs = conf.get("use_pargraphs", False)
            self.window = conf.get("window", 0)
            self.stride = conf.get("stride", 0)