package com.example.springboot1.jersey;


import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class EmployeeRepository {
    private List<Employee> employees;

    public EmployeeRepository() {
        employees = new ArrayList<>();
        employees.add(new Employee(1, "Jane"));
        employees.add(new Employee(2, "Jack"));
        employees.add(new Employee(3, "George"));
    }

    public Employee getEmployee(int id) {
        for (Employee emp : employees) {
            if (emp.getId() == id) {
                return emp;
            }
        }
        throw new RuntimeException();
    }

    public void updateEmployee(Employee employee, int id) {
        for (Employee emp : employees) {
            if (emp.getId() == id) {
                emp.setId(employee.getId());
                emp.setName(employee.getName());
                return;
            }
        }
        throw new RuntimeException();
    }

    public void deleteEmployee(int id) {
        for (Employee emp : employees) {
            if (emp.getId() == id) {
                employees.remove(emp);
                return;
            }
        }
        throw new RuntimeException();
    }

    public void addEmployee(Employee employee) {
        for (Employee emp : employees) {
            if (emp.getId() == employee.getId()) {
                throw new RuntimeException();
            }
        }
        employees.add(employee);
    }

    public List<Employee> getEmployees() {
        return employees;
    }

    public void setEmployees(List<Employee> employees) {
        this.employees = employees;
    }
}
