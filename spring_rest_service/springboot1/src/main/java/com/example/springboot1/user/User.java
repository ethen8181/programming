package com.example.springboot1.user;

import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;

import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;

// ApiModel and ApiModelProperty enables custom swagger documentation for the class and field
@ApiModel(description = "Information about the user.")
public class User {
    private Integer id;

    // one important aspect of services to do add proper validation, use the validation.api
    // to add validation and proper message
    @Size(min = 2, message = "Name should have at least 2 characters")
    private String name;

    @Past
    @ApiModelProperty(notes = "Birth date should be in the past")
    private Date birthDate;

    // we'll get no default constructor such as (no Creators, like default construct, exist)
    // if we don't create a dummy constructor after over-riding the default constructor with our own
    User() {

    }

    public User(int id, String name, Date birthDate) {
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

    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", birthDate=" + birthDate +
                '}';
    }
}
