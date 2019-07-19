package com.ethen.kafka1.tutorial2;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;
import javafx.util.Pair;
import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.index.IndexResponse;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestClientBuilder;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.xcontent.XContentType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

/*
    https://www.elastic.co/guide/en/elasticsearch/client/java-rest/7.1/java-rest-high.html
 */
public class ElasticSearchConsumer {

    Logger logger = LoggerFactory.getLogger(ElasticSearchConsumer.class.getName());

    int port = 443; // localhost 9200
    String httpScheme = "https";

    String index = "twitter";  // we'll need to PUT /twitter to create the index first (we can use bonsai console)

    String hostname = ""; // localhost or bonsai url
    String username = ""; // needed only for bonsai
    String password = ""; // needed only for bonsai

    String bootstrapServers = "127.0.0.1:9092";
    String groupId = "kafka-demo-elasticsearch";
    String topic = "twitter_tweets";

    /*
        bin/kafka-consumer-groups.sh \
        --bootstrap-server localhost:9092 \
        --group kafka-demo-elasticsearch \
        --describe
     */
    public static void main(String[] args) {
        new ElasticSearchConsumer().run();
    }

    private void run() {
        RestHighLevelClient client = createClient();
        KafkaConsumer<String, String> consumer = createKafkaConsumer();

        // poll for new data and insert them into elasticsearch
        advanceConsume(client, consumer);
    }

    /*
        When inserting documents into elasticsearch, we can leave out the id of the document and
        only provide the index and type, but if we wish to make our consumer idempotent, i.e.
        no duplicated messages end up in elasticsearch, we should provide the id ourselves

        we can use a generic kafka id, i.e. record.topic() + record.partition() + record.offset(),
        as each message can be uniquely identified with these three factors.

        Or we can find a twitter specific id

        ------------------------------------
        we set ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG to false
        accumulate records into a buffer then flushing the buffer to a database + committing the offsets manually

        ------------------------------------
        elasticsearch has API for performing bulk insert
     */
    private void advanceConsume(RestHighLevelClient client, KafkaConsumer<String, String> consumer) {
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            int recordCount = records.count();
            logger.info("Received " + recordCount + " records");

            if (recordCount > 0) {
                BulkRequest bulkRequest = new BulkRequest();
                for (ConsumerRecord<String, String> record: records) {
                    Pair<String, String> pair = extractValidTweetJsonStringAndId(record.value());
                    String id = pair.getKey();
                    if (id != null) {
                        IndexRequest indexRequest = new IndexRequest(index, "_doc", id)
                            .source(pair.getValue(), XContentType.JSON);
                        bulkRequest.add(indexRequest);
                    }
                }

                try {
                    client.bulk(bulkRequest);
                } catch (IOException e) {
                    logger.error("Error while bulk indexing", e);
                }

                consumer.commitSync();
                logger.info("offsets have been committed");
            }
        }
    }

    /*
        the commit strategy we are employing here is to leverage
        enable.auto.commit=true
        and perform synchronous process of batches, i.e. in our code, after calling .poll
        to retrieve a batch of records then do a for loop over the records to insert it
        into elasticsearch.

        with auto-commit, offsets will be committed automatically for us at a regular interval
        (auto.commit.interval.ms=5000) every time we call .poll
     */
    private void simpleConsume(RestHighLevelClient client, KafkaConsumer<String, String> consumer) {
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record: records) {
                String tweet = extractValidTweetJsonString(record.value());
                IndexRequest indexRequest = new IndexRequest(index, "_doc").source(tweet, XContentType.JSON);

                IndexResponse indexResponse = null;
                try {
                    indexResponse = client.index(indexRequest);
                } catch (IOException e) {
                    logger.error("Error while indexing", e);
                }

                if (indexResponse != null) {
                    // bonsai console to check for inserted documents: /twitter/_doc/[input id]
                    logger.info(indexResponse.getId());
                }
            }
        }
    }

    /*
        We only extract the information that we need from the tweet,
        otherwise we might hit elasticsearch's index.mapping.depth.limit upper limit

        https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
     */
    private String extractValidTweetJsonString(String tweetJsonString) {
        Gson gson = new Gson();
        Tweet tweet = gson.fromJson(tweetJsonString, Tweet.class);
        return gson.toJson(tweet);
    }

    private Pair<String, String> extractValidTweetJsonStringAndId(String tweetJsonString) {
        Gson gson = new Gson();
        Tweet tweet = gson.fromJson(tweetJsonString, Tweet.class);
        return new Pair<>(tweet.getIdStr(), gson.toJson(tweet));
    }

    private KafkaConsumer<String, String> createKafkaConsumer() {
        Properties properties = new Properties();
        properties.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        properties.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        properties.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        properties.setProperty(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        properties.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest"); // or latest
        properties.setProperty(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");

        // create consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(properties);
        consumer.subscribe(Collections.singleton(topic));
        return consumer;
    }

    /*
        https://www.elastic.co/guide/en/elasticsearch/client/java-rest/7.1/_basic_authentication.html
     */
    private RestHighLevelClient createClient() {
        CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
        credentialsProvider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials(username, password));

        RestClientBuilder builder = RestClient.builder(new HttpHost(hostname, port, httpScheme))
            .setHttpClientConfigCallback(new RestClientBuilder.HttpClientConfigCallback() {
                @Override
                public HttpAsyncClientBuilder customizeHttpClient(HttpAsyncClientBuilder httpAsyncClientBuilder) {
                    return httpAsyncClientBuilder.setDefaultCredentialsProvider(credentialsProvider);
                }
            });
        return new RestHighLevelClient(builder);
    }
}


// https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
class Tweet {

    // https://stackoverflow.com/questions/28957285/what-is-the-basic-purpose-of-serializedname-annotation-in-android-using-gson
    @SerializedName("created_at")
    private String createdAt;

    @SerializedName("id_str")
    private String idStr;
    private String text;

    public String getCreatedAt() {
        return createdAt;
    }

    public String getIdStr() {
        return idStr;
    }

    public String getText() {
        return text;
    }
}