


GET tmdb/_doc/_search 
{
    "query": {
        "function_score": {
            "query": {
                "multi_match": {
                    "query": "william shatner patrick stewart",
                    "type": "cross_fields",
                    "fields": [
                        "overview",
                        "title",
                        "directors.name",
                        "cast.name"
                    ]
                }
            },
            "functions": [
                {
                    "weight": 2.5,
                    "filter": {
                        "term": {
                            "title": "star trek"
                        }
                    }
                }   
            ]
        }
    }
}

DELETE tmdb

PUT tmdb
{
    "settings": {
        "index": {
            "number_of_replicas": 1,
            "number_of_shards": 1
        },
        "analysis": {
            "filter": {
                "bigram_filter": {
                    "type": "shingle",
                    "max_shingle_size": 2,
                    "min_shingle_size": 2,
                    "output_unigrams": false
                }
            },
            "analyzer": {
                "default": {
                    "type": "english"
                },
                "english_bigram": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "bigram_filter"
                    ]
                }
            }
        }
    }
}