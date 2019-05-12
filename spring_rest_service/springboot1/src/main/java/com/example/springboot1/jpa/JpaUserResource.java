package com.example.springboot1.jpa;

import com.example.springboot1.user.UserNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.hateoas.Resource;
import org.springframework.hateoas.mvc.ControllerLinkBuilder;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.net.URI;
import java.util.List;
import java.util.Optional;

import static org.springframework.hateoas.mvc.ControllerLinkBuilder.linkTo;
import static org.springframework.hateoas.mvc.ControllerLinkBuilder.methodOn;

/*
    The core API is to create a Resource or Controller, annotate it with RestController
    and create the GET, POST, etc. Mapping for the various business logic for each type of request

    This RestController retrieves data from JPA instead of the static in-memory arraylist
 */
@RestController
public class JpaUserResource {

    @Autowired
    private JpaUserRepository jpaUserRepository;

    @Autowired
    private JpaPostRepository jpaPostRepository;

    @GetMapping("/jpa/users")
    public List<JpaUser> retrieveAllUsers() {
        return jpaUserRepository.findAll();
    }

    /*
        An interesting concept is HATEOAS (hypermedia as the engine of application state).
        It means that the rest service will provide relevant links with the response to help the
        client navigate the REST service more effectively.

        https://spring.io/understanding/HATEOAS
     */
    @GetMapping("/jpa/users/{id}")
    public Resource<JpaUser> retrieveUser(@PathVariable int id) {
        Optional<JpaUser> user = jpaUserRepository.findById(id);
        if (!user.isPresent()) throw new UserNotFoundException("id-" + id);

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
        Resource<JpaUser> resource = new Resource<>(user.get());
        ControllerLinkBuilder linkTo = linkTo(methodOn(this.getClass()).retrieveAllUsers());
        resource.add(linkTo.withRel("all-users")); // we need to specify the name for the hateoas

        //return user;
        return resource;
    }

    @DeleteMapping("/jpa/users/{id}")
    public void deleteUser(@PathVariable int id) {
        jpaUserRepository.deleteById(id);
    }

    /*
        - we can use postman to test out our POST request
        - we follow the HTTP standard of returning 201 created for POST methods
        - we also return the actual url/location of the POST request, i.e. the location
        of the new resource which was created by the request in the HEADER of the response

        https://stackoverflow.com/questions/22669447/how-to-return-a-relative-uri-location-header-with-flask

        We've also added the @Valid annotation to use the validation we've added for User
     */
    @PostMapping("/jpa/users")
    public ResponseEntity createUser(@Valid @RequestBody JpaUser user) {
        JpaUser savedUser = jpaUserRepository.save(user);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest() // avoid hard-coding the POST url
            .path("/{id}")
            .buildAndExpand(savedUser.getId())
            .toUri();

        return ResponseEntity.created(location).build(); // ResponseEntity.status(201).build();
    }


    @GetMapping("/jpa/users/{id}/posts")
    public List<JpaPost> retrieveUserPosts(@PathVariable int id) {
        Optional<JpaUser> optionalJpaUser = jpaUserRepository.findById(id);
        if (!optionalJpaUser.isPresent()) throw new UserNotFoundException("id-" + id);
        return optionalJpaUser.get().getJpaPosts();
    }

    @PostMapping("/jpa/users/{id}/posts")
    public ResponseEntity createPost(@PathVariable int id, @RequestBody JpaPost jpaPost) {
        Optional<JpaUser> optionalJpaUser = jpaUserRepository.findById(id);
        if (!optionalJpaUser.isPresent()) throw new UserNotFoundException("id-" + id);

        JpaUser jpaUser = optionalJpaUser.get();
        jpaPost.setJpaUser(jpaUser); // remember to set the user before saving it to the database
        jpaPostRepository.save(jpaPost);

        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest() // avoid hard-coding the POST url
            .path("/{id}")
            .buildAndExpand(jpaPost.getId())
            .toUri();

        return ResponseEntity.created(location).build(); // ResponseEntity.status(201).build();
    }

}
