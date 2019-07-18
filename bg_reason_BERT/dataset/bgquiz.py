import json


class Question(object):
    def __init__(self, id, qid, question, answers, correct, category, url):
        self.id = id
        self.qid = qid
        self.question = question
        self.answers = answers
        self.correct = correct
        self.category = category
        self.url = url

    @classmethod
    def from_dict(cls, json_object):
        q = cls(json_object['id'], json_object['qid'], json_object['question'], json_object['answers'],
                json_object['correct'], json_object['category'], json_object['url'])

        return q


class BGQuiz(object):

    def __init__(self, path):
        with open(path, "r") as f:
            json_data = json.load(f)
            self._data_gen = []

            for (category, items) in json_data['data'].items():
                for questions in items:
                    for q in questions['questions']:
                        q['category'] = category
                        q['url'] = questions['url']
                        self._data_gen.append(Question.from_dict(q))

    def iterator(self):
        return (x for x in self._data_gen)

    def size(self):
        return len(self._data_gen)