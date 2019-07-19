package com.example.springboot1.jersey;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

/*
    JAX-RS (Java API for RESTful Web Services) is a Java programming language API
    specification for developing web services according to the REST pattern.
    Jersey is an open source framework for developing RESTful Web Services in Java,
    and it is a reference implementation of the JAX-RS specification.

    https://www.baeldung.com/jax-rs-response
    http://zetcode.com/springboot/jersey/
    https://www.baeldung.com/jersey-rest-api-with-spring

    the @Path annotation provides the relative URI path to the service.
 */
@Component
@Path("/employees")
public class EmployeeService {

    @Autowired
    private EmployeeRepository employeeRepository;

    /*
        An example GET request, where we specified we'll return a Json Response
        In the Response we pass in our entities, which is a list of employees POJO

        the @Produces annotation defines the endpoint's response type
     */
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllEmployees() {
        return Response.ok(employeeRepository.getEmployees()).build();
    }

    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getEmployee(@PathParam("id") int id) {
        // showing an alternative API for writing response
        return Response
            .status(Response.Status.OK)
            .entity(employeeRepository.getEmployee(id))
            .build();
    }
}
