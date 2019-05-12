package com.example.springboot1.entity;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

/*
    We want to leverage JPA and map this bean to a table,
    to do so we'll add the @Entity annotation
 */
@Entity
public class EntityUser {

    // marking id as the primary key and will be auto-generated
    @Id
    @GeneratedValue
    private long id;
    private String name;
    private String role;

    public EntityUser() {

    }

    public EntityUser(String name, String role) {
        this.name = name;
        this.role = role;
    }

    public long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getRole() {
        return role;
    }

    @Override
    public String toString() {
        return "EntityUser{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", role='" + role + '\'' +
                '}';
    }
}
