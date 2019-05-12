package com.example.springboot1.entity;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/*
    CommandLineRunner is a Spring Boot interface with a run method. Spring Boot will automatically
    call the run method of all beans implementing this interface after the application context
    has been loaded.

    We use it here to test out our EntityUserDaoService.
    But the typical use-case for this when we wish to execute some piece of code exactly before the
    application startup completes. e.g. use it to source some data beforehand.

    https://www.baeldung.com/spring-boot-console-app
 */
@Component
public class EntityUserCommandLineRunner implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(EntityUserCommandLineRunner.class);

    @Autowired
    private EntityUserRepository entityUserRepository;

    @Override
    public void run(String... args) throws Exception {
        /*
            If we turn on spring.jpa.show-sql=true in the property file,
            we can see the following information in the log

            create table entity_user (id bigint not null, name varchar(255), role varchar(255), primary key (id))
            insert into entity_user (name, role, id) values (?, ?, ?)

            This is h2 in-memory database in action
         */
        EntityUser entityUser = new EntityUser("Jack", "Admin");
        entityUserRepository.save(entityUser);
        log.info("New user is created : " + entityUser);
    }
}
