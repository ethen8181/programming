package com.example.springboot1.entity;


import org.springframework.data.jpa.repository.JpaRepository;

/*
    JpaRepository acts as a shortcut to manage our entities without having to write our own DaoService
    We need to provide the entity that we wish to manage and the type of the primary key
 */
public interface EntityUserRepository extends JpaRepository<EntityUser, Long> {
}
