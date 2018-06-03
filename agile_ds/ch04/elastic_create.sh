# starting from elasticsearch 6.0, we need to add the content type information
# https://www.elastic.co/blog/strict-content-type-checking-for-elasticsearch-rest-requests
curl -XPUT 'http://localhost:9200/agile_data_science/' -d '{
    "settings" : {
        "index" : {
            "number_of_shards" : 1,
            "number_of_replicas" : 1
        }
    }
}' -H 'Content-Type: application/json'
