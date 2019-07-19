package com.example.springboot1.helloworld;


import org.springframework.web.bind.annotation.*;

/*
    Define the method, e.g. GET
    Define a URI, e.g. /hello-world
 */
@RestController
public class HelloWorldController {

    // a GET request that returns a dummy string
    @RequestMapping(method = RequestMethod.GET, path = "/hello-world")
    public String helloWorld() {
        return "Hello World";
    }

    // a GET request that returns a bean, notice that GetMapping is a shorter way to define GET
    @GetMapping("/hello-world-bean")
    public HelloWorldBean helloWorldBean() {
        return new HelloWorldBean("Hello World Bean");
    }

    // adding a path variable to the uri
    @GetMapping("/hello-world/path-variable/{name}")
    public HelloWorldBean helloWorldPathVariable(@PathVariable String name) {
        return new HelloWorldBean(String.format("Hello World , %s", name));
    }
}
