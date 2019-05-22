# BG Reason with BERT

## Filling ElasticSearch with Wikipedia

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
