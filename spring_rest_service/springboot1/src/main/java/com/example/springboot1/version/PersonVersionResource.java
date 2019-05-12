package com.example.springboot1.version;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/*
    How to create different versions for our API,
    in this case version 1 is returning the person's name
    whereas in version 2, it is returning the first and last name separately
 */
@RestController
public class PersonVersionResource {

    // URI versioning, we use v1 and v2 in the URI to differentiate results between versions
    @GetMapping("person/v1")
    public PersonV1 personV1() {
        return new PersonV1("Bob Charlie");
    }

    @GetMapping("person/v2")
    public PersonV2 personV2() {
        return new PersonV2(new Name("Bob", "Charlie"));
    }

    // URI parameter versioning, we pass the version as a query parameter
    // e.g. http://localhost:8080/person/param?version=1
    @GetMapping(value = "person/param", params = "version=1")
    public PersonV1 paramV1() {
        return new PersonV1("Bob Charlie");
    }

    @GetMapping(value = "person/param", params = "version=2")
    public PersonV2 paramV2() {
        return new PersonV2(new Name("Bob", "Charlie"));
    }

    // header versioning
    // in the headers section, we would need to add X-API-VERSION as the key and 1 as the value
    @GetMapping(value = "person/header", headers = "X-API-VERSION=1")
    public PersonV1 headerV1() {
        return new PersonV1("Bob Charlie");
    }

    @GetMapping(value = "person/header", headers = "X-API-VERSION=2")
    public PersonV2 headerV2() {
        return new PersonV2(new Name("Bob", "Charlie"));
    }

    // accept header versioning
    // in the header section, we would need to add Accept as the key and value application/company.app-v1+json
    @GetMapping(value = "person/produces", produces = "application/company.app-v1+json")
    public PersonV1 producesV1() {
        return new PersonV1("Bob Charlie");
    }

    @GetMapping(value = "person/produces", produces = "application/company.app-v2+json")
    public PersonV2 producesV2() {
        return new PersonV2(new Name("Bob", "Charlie"));
    }
}
