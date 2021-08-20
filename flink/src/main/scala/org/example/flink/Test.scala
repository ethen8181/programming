package org.example.flink

import org.apache.flink.streaming.api.scala.StreamExecutionEnvironment

object Test extends App {
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    println("test")
}
