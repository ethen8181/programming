package com.example.springboot1;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication
public class Springboot1Application {

	public static void main(String[] args) {

	    // when we start the spring boot application it would trigger the auto-configuration process
        // and start creating beans
        ApplicationContext context = SpringApplication.run(Springboot1Application.class, args);
    }

}
