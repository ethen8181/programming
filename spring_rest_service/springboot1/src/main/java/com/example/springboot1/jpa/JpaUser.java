package com.example.springboot1.jpa;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.OneToMany;
import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;
import java.util.List;

/*
    ApiModel and ApiModelProperty enables custom swagger documentation for the class and field
    We add the entity annotation to leverage JPA

    Spring boot will automatically perform a lot of magic underneath of hood for us, but if we
    need some finer grained control, that's when we can use the data.sql and schema.sql files.

    by default Spring boot will create empty table for us, to populate it with some initial values
    we can create a file called data.sql under for application.properties file.
    Remember to use single quotes for string in that sql file

    https://www.baeldung.com/spring-boot-data-sql-and-schema-sql
 */
@ApiModel(description = "Information about the user.")
@Entity
public class JpaUser {
    @Id
    @GeneratedValue
    private Integer id;

    // one important aspect of services to do add proper validation, use the validation.api
    // to add validation and proper message
    @Size(min = 2, message = "Name should have at least 2 characters")
    private String name;

    @Past
    @ApiModelProperty(notes = "Birth date should be in the past")
    private Date birthDate;

    /*
        Configure mappedBy to indicate which this the field that's owning the relationship.
        we don't want to create the relationship column in both places.

        We'll see something like this in the logs, where jpa_user_id is the foreign key that links the post back to
        the user that created it.

        create table jpa_post (id integer not null, description varchar(255), jpa_user_id integer, primary key (id))
        create table jpa_user (id integer not null, birth_date timestamp, name varchar(255), primary key (id))
     */
    @OneToMany(mappedBy = "jpaUser")
    private List<JpaPost> jpaPosts;

    // we'll get no default constructor such as (no Creators, like default construct, exist)
    // if we don't create a dummy constructor after over-riding the default constructor with our own
    JpaUser() {

    }

    public JpaUser(int id, String name, Date birthDate) {
        this.id = id;
        this.name = name;
        this.birthDate = birthDate;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Date getBirthDate() {
        return birthDate;
    }

    public void setBirthDate(Date birthDate) {
        this.birthDate = birthDate;
    }

    public List<JpaPost> getJpaPosts() {
        return jpaPosts;
    }

    public void setJpaPosts(List<JpaPost> jpaPosts) {
        this.jpaPosts = jpaPosts;
    }

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", birthDate=" + birthDate +
                '}';
    }
}

