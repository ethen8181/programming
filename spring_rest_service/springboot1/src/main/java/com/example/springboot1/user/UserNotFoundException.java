package com.example.springboot1.user;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/*
    Annotate UserNotFoundException with ResponseStatus to be a 404 not found status,
    i.e. whenever we throw the UserNotFoundException, the HTTP status that is returned will be 404

    Note that if we wish to have a uniform exception class, we would implement the
    ResponseEntityExceptionHandler and annotate it with ControllerAdvice
 */
@ResponseStatus(HttpStatus.NOT_FOUND)
public class UserNotFoundException extends RuntimeException {

    public UserNotFoundException(String message) {
        super(message);
    }
}
