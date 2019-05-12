package com.example.springboot1.user;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.hateoas.Resource;
import org.springframework.hateoas.mvc.ControllerLinkBuilder;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.net.URI;
import java.util.List;

import static org.springframework.hateoas.mvc.ControllerLinkBuilder.*;

/*
    The core API is to create a Resource or Controller, annotate it with RestController
    and create the GET, POST, etc. Mapping for the various business logic for each type of request
 */
@RestController
public class UserResource {

    @Autowired
    private UserDaoService service;

    @GetMapping("/users")
    public List<User> retrieveAllUsers() {
        return service.findAll();
    }

    /*
        An interesting concept is HATEOAS (hypermedia as the engine of application state).
        It means that the rest service will provide relevant links with the response to help the
        client navigate the REST service more effectively.

        https://spring.io/understanding/HATEOAS
     */
    @GetMapping("/users/{id}")
    public Resource<User> retrieveUser(@PathVariable int id) {
        User user = service.findOne(id);
        if (user == null) throw new UserNotFoundException("id-" + id);

        /*
            we'll add the link that gets all the users with the response. This is what the JSON
            response would look like

            {
                "id": 1,
                "name": "Adam",
                "birthDate": "2019-05-06T21:14:16.195+0000",
                "_links": {
                    "all-users": {
                        "href": "http://localhost:8080/users"
                    }
                }
            }
         */
        Resource<User> resource = new Resource<>(user);
        ControllerLinkBuilder linkTo = linkTo(methodOn(this.getClass()).retrieveAllUsers());
        resource.add(linkTo.withRel("all-users")); // we need to specify the name for the hateoas

        //return user;
        return resource;
    }

    @DeleteMapping("/users/{id}")
    public void deleteUser(@PathVariable int id) {
        User user = service.deleteById(id);
        if (user == null) throw new UserNotFoundException("id-" + id);
    }

    /*
        - we can use postman to test out our POST request
        - we follow the HTTP standard of returning 201 created for POST methods
        - we also return the actual url/location of the POST request, i.e. the location
        of the new resource which was created by the request in the HEADER of the response

        https://stackoverflow.com/questions/22669447/how-to-return-a-relative-uri-location-header-with-flask

        We've also added the @Valid annotation to use the validation we've added for User
     */
    @PostMapping("/users")
    public ResponseEntity createUser(@Valid @RequestBody User user) {
        User savedUser = service.save(user);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest() // avoid hard-coding the POST url
            .path("/{id}")
            .buildAndExpand(savedUser.getId())
            .toUri();

        return ResponseEntity.created(location).build(); // ResponseEntity.status(201).build();
    }

}
