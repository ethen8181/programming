package com.example.springboot1.user;


import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;

/*
    Data Access Object (DAO)
    https://www.baeldung.com/java-dao-pattern

    We'll switch all of these to talking with JPA, a proper database once we learn about them.
    For now we'll store all of our data inside the memory using a static ArrayList

    http://zetcode.com/springboot/component/
 */
@Component
public class UserDaoService {

    private static List<User> users = new ArrayList<>();

    // use to mimic auto-increment id
    private static int userCount = 3;

    static {
        users.add(new User(1, "Adam", new Date()));
        users.add(new User(2, "Eve", new Date()));
        users.add(new User(3, "Jack", new Date()));
    }

    public List<User> findAll() {
        return users;
    }

    public User save(User user) {
        if (user.getId() == null) {
            user.setId(++userCount);
        }
        users.add(user);
        return user;
    }

    public User findOne(int id) {
        for (User user: users) {
            if (user.getId() == id) {
                return user;
            }
        }
        return null;
    }

    public User deleteById(int id) {
        /*
            We use an iterator to remove a single element while looping through
            the arraylist to avoid the ConcurrentModificationException (it's an
            exception that's used to fail fast when something we are iterating on
            is modified)

            https://www.baeldung.com/java-concurrentmodificationexception
         */
        Iterator<User> iterator = users.iterator();
        while (iterator.hasNext()) {
            User user = iterator.next();
            if (user.getId() == id) {
                iterator.remove();
                return user;
            }
        }
        return null;
    }
}
