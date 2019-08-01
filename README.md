# Beyond English-only Reading Comprehension
Experiments in Zero-Shot Multilingual Transfer for Bulgarian

## Dataset

Our goal is to build a task in a low-resource language, such as Bulgarian, as close as possible to the multiple-choice reading comprehension in a high-resource language such as English. The dataset can be downloaded from [this link](https://github.com/mhardalov/bg-reason-BERT/blob/master/data/bg_rc-v1.0.json).

| Domain | #QA-paris | #Choices | Len Question | Len Options | Vocab Size |
|:-------|:---------:|:--------:|:------------:|:-----------:|:----------:|
| **12th Grade Matriculation Exam** |
| Biology | 437 | 4 | 10.44 | 2.64 | 2,414 (12,922)|
| Philosophy | 630 | 4 | 8.91 | 2.94| 3,636  (20,392) |
| Geography | 612 | 4 | 12.83 | 2.47 | 3,239 (17,668) |
| History | 542 | 4 | 23.74 | 3.64 | 5,466 (20,456) |
| **Online History Quizzes** |
| Bulgarian History | 229 | 4 | 14.05 | 2.80 | 2,287 (10,620) |
| PzHistory | 183 | 3 | 38.89 | 2.44 | 1,261 (7,518) |
| **Total** | 2,633 | 3.93 | 15.67 | 2.89 | 13,329 (56,104) |

## Evaluation

To evaluate the models we have built an evaluation script, allowing easy performance measrument of the predicted results.
To run the evaluation, use:

```python
python evaluate.py data/bg_rc-v1.0.json experiments/preds.json
```

The prediction file should be in the following format:

```
{
  "id": "predicted_answer",
  ...
  "id": "predicted_answer"
}
 ```
 
## Running the model

### Filling ElasticSearch with Wikipedia

#### Create wikidump

First, we need to download a [Wikipedia database dump](http://download.wikimedia.org/) for Bulgarian. (e.g. https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/bgwiki/20190501/bgwiki-20190501-pages-meta-current.xml.bz2)

Next step is to convert the xml into well-structured JSON with [WikiExtractor](https://github.com/attardi/wikiextractor).

```bash
python WikiExtractor.py ---output bgwiki.json --json /path/to/bgwiki-*-current.xml 
```

This should produce a folder with the following format: `AA`, `AB`,..., `ZZ`

#### Fill the index

Download ES (Tested with 7.0.1) from the [official web site](https://www.elastic.co/downloads/elasticsearch).

Start an instance:

```bash
./elasticsearch-7.0.1/bin/elasticsearch
```
Create ElasticSearch filler config file:
```json
{
   "host":"localhost",
   "port":"9200",
   "index_name":"bgwiki_test",
   "batch_size":10000,
   "es_schema":{
      "settings":{
         "max_ngram_diff":3,
         "analysis":{
            "analyzer":{
               "my_analyzer":{
                  "tokenizer":"my_tokenizer"
               }
            },
            "tokenizer":{
               "my_tokenizer":{
                  "type":"ngram",
                  "min_gram":1,
                  "max_gram":3,
                  "token_chars":[
                     "whitespace",
                     "punctuation"
                  ]
               }
            }
         }
      },
      "mappings":{
         "properties":{
            "title":{
               "type":"text",
               "fields":{
                  "ngram":{
                     "type":"text",
                     "analyzer":"my_analyzer"
                  },
                  "bulgarian":{
                     "type":"text",
                     "analyzer":"bulgarian"
                  }
               }
            },
            "passage":{
               "type":"text",
               "fields":{
                  "ngram":{
                     "type":"text",
                     "analyzer":"my_analyzer"
                  },
                  "bulgarian":{
                     "type":"text",
                     "analyzer":"bulgarian"
                  }
               }
            },
            "page":{
               "type":"long"
            },
            "isbn":{
               "type":"text"
            },
            "timestamp":{
               "type":"date",
               "format":"strict_date_optional_time||epoch_millis"
            }
         }
      }
   }
}
```

Fill the inverted index:
```bash 
python fill_elastic.py --wiki_path /PATH/TO/WIKI_EXTRACTOR_DIRS --es_config_file ./configs/bgwiki.json 
```

### Running the prediction pipeline



## Cite

TBD
