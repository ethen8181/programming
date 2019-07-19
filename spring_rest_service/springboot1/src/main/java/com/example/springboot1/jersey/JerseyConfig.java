package com.example.springboot1.jersey;

import org.glassfish.jersey.server.ResourceConfig;
import org.springframework.context.annotation.Configuration;


/*
    For every service that we've created using Jersey, this syntax
    is required to register the service class
 */
@Configuration
public class JerseyConfig extends ResourceConfig {
    public JerseyConfig() {
        register(EmployeeService.class);
    }
}
