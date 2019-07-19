package com.example.springboot1.jersey;

import javax.xml.bind.annotation.XmlRootElement;

/*
    the @XmlRootElement annotation is only required if XML support is needed
    (in additional to JSON)
 */
@XmlRootElement
public class Employee {
    private int id;
    private String name;

    public Employee() {}

    public Employee(int id, String name) {
        this.id = id;
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
