package com.example.springboot1.entity;

import org.springframework.stereotype.Repository;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.transaction.Transactional;


/*
    Repository annotation denotes something that interacts with the database.

    Transactional annotation makes each method transactional.

    EntityManager like its name states, manages entity.
    After we call .persist, it is in something called a persistence context
    EntityManager only tracks object that are persisted.

    Although feasible, this way of doing things creates a bunch of boilerplate code,
    because we have to implement insert, delete, etc for every one of our bean.
    The UserRepository interface aims to solve this.
 */
@Repository
@Transactional
public class EntityUserDaoService {

    @PersistenceContext
    private EntityManager entityManager;

    /*
        Example:
        EntityUser entityUser = new EntityUser("Jack", "Admin");
        long id = entityUserDaoService.insert(entityUser);
     */
    public long insert(EntityUser entityUser) {
        entityManager.persist(entityUser);
        return entityUser.getId();
    }
}
