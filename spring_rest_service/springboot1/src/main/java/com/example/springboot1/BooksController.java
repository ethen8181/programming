package com.example.springboot1;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;


// After defining the Get method to get all books, we can go to http://localhost:8080/books
// and see our data returned (port 8080 is the default port)
@RestController
public class BooksController {

    @GetMapping("/books")
    public List<Book> getAllBooks() {
        return Arrays.asList(new Book(1L, "Mastering Spring Boot", "ethen"));
    }
}
