package com.ethen.kafka1.tutorial1;

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class ProducerDemo {

    // typing psvm gives us a shortcut for the main method
    public static void main(String[] args) {

        final Logger logger = LoggerFactory.getLogger(ProducerDemo.class);

        // step 1: create producer properties
        // https://kafka.apache.org/documentation/#producerconfigs
        Properties properties = new Properties();

        // we can type in the string name of the property field ourselves, but the recommended approach
        // is to use the static field from ProducerConfig to prevent fat-finger the wrong thing
        // properties.setProperty("bootstrap.servers", "127.0.0.1:9092");
        properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "127.0.0.1:9092");

        // kafka serializes the key and value as bytes before sending them over the network
        properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // step 2: create the producer
        KafkaProducer<String, String> producer = new KafkaProducer<>(properties);

        // step 3: send data
        // by supplying the key, we ensure that records of the same key will always goes to the same partition
        String topic = "first_topic";
        String key = "id_1";
        String value = "new message 1";
        ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, value);

        // producer.send(record);
        // we can add callbacks to our send method to implement additional logic whenever
        // a record is successfully sent or an exception is thrown
        producer.send(record, new Callback() {
            public void onCompletion(RecordMetadata recordMetadata, Exception e) {
                if (e == null) {
                    logger.info("Received new metadata. \n" +
                                "Topic: " + recordMetadata.topic() + "\n" +
                                "Partition: " + recordMetadata.partition() + "\n" +
                                "Offset: " + recordMetadata.offset() + "\n" +
                                "Timestamp: " + recordMetadata.timestamp());
                } else {
                    logger.error("Error while producing", e);
                }
            }
        });

        // as send is an asynchronous procedure (happens in the background),
        // we need to remember to flush or close the producer
        producer.close();
        logger.info("End of application");
    }
}
