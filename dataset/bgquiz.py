import json


class BGQuiz(object):

    def __init__(self, paths):
        self.json_data = []
        for path in paths:
            with open(path, "r") as f:
                self.json_data += json.load(f)
