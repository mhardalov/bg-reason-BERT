from reasoning.span import predict_span


def query_es(es, query, index_name, num_hits=1, query_field='passage', highligh_size=400, num_highlights=3,
             explain=False):
    #     res = es.search(index=name, body={"query": {"match": { query_field: query }},
    #                                               'from': 0, 'size': num_hits})

    res = es.search(
        index=index_name,
        body={
            "explain": explain,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": query_field,
                }
            },
            "highlight": {
                "fragment_size": highligh_size,
                "type": "plain",
                "number_of_fragments": num_highlights,
                "fields": {
                    "passage": {}
                }
            },
            "from": 0,
            "size": num_hits
        })
    #     return res
    #     scores = [hit['_score'] for hit in res['hits']['hits']]

    return [{
        "score":
            x['_score'],
        "source":
            x['_source'],
        "highlight":
            x['highlight']['passage'] if hasattr(x, 'highlight') else ''
    } for x in res['hits']['hits']]


def qa(es,
       index_name,
       model,
       tokenizer,
       question,
       num_hits=1,
       query_field=[
           'title', 'title.ngram', 'title.bulgarian', 'passage.ngram^2',
           'passage', 'passage.bulgarian^2'
       ],
       use_gpu=False,
       batch_size=32):
    res = query_es(
        es,
        question,
        index_name,
        num_hits,
        query_field=query_field,
        explain=False)

    rankings = []
    wikis = [[]]
    i = 0
    for r in res:
        #         for wiki in r['source']:
        passage = r['source']['passage']
        passage = passage.replace('<em>', '').replace('</em>', '')

        if len(wikis[i]) >= batch_size:
            i += 1
            wikis.append([])

        wikis[i].append(passage)
        rankings.append((0, r['source']['title']))

    #         n = 400
    #         for wiki in [passage[i:i+n] for i in range(0, len(passage), n)]:
    #             pred = predict(model, tokenizer, question, wiki)
    # #             print(wiki, pred)
    #             if len(pred[0]):
    #                 rankings.append(pred + (r['source']['title'], ))
    i = 0
    for batch in wikis:
        for pred in predict_span(model, tokenizer, zip([question] * len(batch), batch), use_gpu=use_gpu):

            rankings[i] = pred + (rankings[i][1],)
            i += 1

    rankings = list(sorted(filter(lambda x: len(x[0]), rankings), key=lambda x: x[1], reverse=True))

    return rankings
