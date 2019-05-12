package com.example.springboot1.jpa;

import com.fasterxml.jackson.annotation.JsonIgnore;

import javax.persistence.*;

@Entity
public class JpaPost {

    @Id
    @GeneratedValue
    private Integer id;
    private String description;

    /*
         Define the many to one relationship between post and user (a user can create many posts)
         and define the lazy fetch behaviour so that it won't fetch the corresponding user unless
         we explicitly calls getJpaUser.

         The JsonIgnore annotation prevents the recursive loop where JpaUser tries to return a list
         of posts to the response and JpaPost returns the JpaUser to the response.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JsonIgnore
    private JpaUser jpaUser;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public JpaUser getJpaUser() {
        return jpaUser;
    }

    public void setJpaUser(JpaUser jpaUser) {
        this.jpaUser = jpaUser;
    }

    @Override
    public String toString() {
        return "JpaPost{" +
                "id=" + id +
                ", description='" + description + '\'' +
                '}';
    }
}
