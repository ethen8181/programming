package com.example.springboot1.jersey;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringRunner;

import static org.junit.Assert.*;


/*
    An example SpringBootTest involves setting up the @RunWith and SpringBootTest annotation
 */
@RunWith(SpringRunner.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class EmployeeServiceTest {

    // then we leverage the TestRestTemplate class and call .getForEntity to retrieve the entity
    // for a given endpoint. The .getForEntity method is for GET methods
    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    public void getAllEmployees() {
    }

    @Test
    public void getEmployee() {
        ResponseEntity<Employee> responseEntity = restTemplate.getForEntity("/employees/1", Employee.class);
        Employee body = responseEntity.getBody();

        assertEquals(responseEntity.getStatusCodeValue(), 200);
        assertEquals(body.getId(), 1);
        assertEquals(body.getName(), "Jane");
    }
}