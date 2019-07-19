# Master Java Web Services and REST API with Spring Boot

## BackGround

Spring Project can be composed of many different components. e.g.

- Spring Boot is one of the most popular framework to develop microservices.
- Spring Batch is used to develop batch applications as not every logic is done online.


The reason for Spring framework's popularity are:

- Enables testable code.
- No plumbing code. i.e. removes a lot of boilerplate code such as try/catch/finally that we had to write.
- Flexible architecture. It has components for a wide variety of use-cases.
- Stay current. It's keeping up with the latest trend and develop corresponding components.


The trend is that instead of building 1 monolithic application, we're buiding multiple small applications, hence the term microservices. Upong seeing this trend, Spring Boot's goal is to enable developers to build production ready applications quickly by providing common non-functional features such as embedded servers, metrics, health checks and externalized configurations.

Diving a little bit more in-depth on its features.

- It provides quick starter projects with auto-configuration. Once we start up the quick starter projects we get a lot of stuff that we originally had to manually configure for free. Some more details on auto-configuration. https://aboullaite.me/the-magic-behind-the-magic-spring-boot-autoconfiguration/
- Embedded Server. The old way of deploying our applications used to go like this: we spin up let's say a linux machine, we install a server on that machine only then do we deploy our web application on it. With Spring Boot, we can package our servers, such as Tomcat along with our application.


## Spring VS Spring Boot VS Spring MVC

https://www.springboottutorial.com/spring-boot-vs-spring-mvc-vs-spring

The most important feature of the Spring Framework is Dependency Injection (or so called IOC, Inversion of Control). By letting Spring Framework handle the dependencies for us, we can develop loosely coupled applications that are easily unit-tested.

Spring MVC Framework provides decoupled ways of developing web applications. With concepts such as Dispatcher Servlet, ModelAndView and View Resolver.

And with Spring Boot, we check rid of the need to configure a bunch of stuff with Spring based applications.


## Setting Up a Spring Project

A quick way to launch a spring project. https://start.spring.io/
To generate a Spring Boot quick starter project, we can add Web to the dependencies section.

After specifying some options such as the group id and artifact id, we can download a zip file with contains the project structure for spring.


## Dispatcher Servlet

Dispatcher Servlet is the front controller for the Spring MVC framework. Once it gets a request, it automatically figures out which controller is the appropriate controller to handle that request. After it identifies which controller is most suitable for the request at hand, it then figures out how to package the response back to the client (the `@RestController` annotation contains `@ResponseBody` annotation that knows how to perform the conversion).

HttpMessageConvertersAutoConfiguration, JacksonAutoConfiguration was auto-configured as it was found in the classpath and this was handling the conversion between our bean and the final json-like output that we see in the browser.


## Advanced Features

After setting up the basic REST service, e.g. having the capability to GET, POST, DELETE. There're some advanced topics that are worth understanding, such as:

### Internationalize

Customizing services for different people around the world.

### Content negotiation

Sometimes in a request, there would be an `Accept` key, typically with the value of `application/json`. If we were to change the value to `application/xml`, then the request will most probably return a 406 Not Acceptable status code. With Spring, we can add the support by adding an additional `jackson-dataformat-xml` dependency ...

### Swagger Documentation

- info: Provides a high-level overview of the API that we're offering.
- host: Where we are hosting the service.
- basePath: Self-explanatory. Base path of the service.
- paths: Details of all the resources that we're exposing and the different operations that can be performed on each of the resources.

After adding the doc, it can be accessed at http://localhost:8080/swagger-ui.html#/

### Monitoring

Spring actuator provides monitoring for our microservices. It is in hal-browser (Hypertext Application Language, it's a format that tries to give a consistent way to hyperlink between resources in our API) format. Note that as it exposes a lot of system information, it's usually a good idea to makes sure these information are kept in the a secure manner.

- https://www.baeldung.com/spring-boot-actuators
- http://localhost:8080/browser/index.html#/actuator


### Versioning.

It's good to plan out a versioning strategy while building an API.

- URI versioning (Twitter)
- Request Parameter versioning (Amazon)
- Header versioning (Microsoft)
- Accept Header versioning (Github)

Choosing an approach to do versioning may require a bit of thought, and people all do it differently as each one has its pros and cons.

- With the URI and Request Parameter approach:
    - We might be "polluting" the URI.
- With the Header and Accept Header approach:
    - We might be mis-using the intention of headers as they weren't meant to be used for versioning.
    - We may lose the opportunity to do caching (as the same URI doesn't mean they are the same request).
    - With this approach we most likely can't test out the service with a browser (the end-user would need to have more technical prowess to look at the data).
    - API documentation might be trickier?

### Security

After adding `spring-boot-starter-security` dependency, our request to the service will fail with a 401, unauthorized error.

To fix it, we need to add the basic authorization to our request. In postman, we can go to the authorization section and add the username `user` and password (when we start up the spring boot application, we'll see something along the lines of Using generated security password: XXX).

Or we can configure the value by providing it in `application.properties`

```
spring.security.user.name=username
spring.security.user.password=password
```

### Filtering JSON content

Say one of our bean contains sensitive information, such as the user's password in it, we want to make sure we are not returning that response when random people request for an information about the user.

## JPA (Java Persistence API)

Another popular option to talk to database in Java is JDBC (Java Database Connectivity). It is built upon concepts like Preparement Statement and ResultSet. Where given a Preparement Statement `update users set username = ? where id = ?`, the values of the query will to inserted into the query using different set of methods. Then results from the query are populated into a ResultSet and we would need to convert that into our object.

JDBC is based on queries which can become complicated and hard to maintain. JPA tries to solve this query-centric approach by allowing us to define mappings between our beans and tables.

And for those curious about the relationship between JPA and Hibernate (one of the most popular ORM framework bundled with Spring). JPA is a interface specification. e.g.

- How do we define entities?
- How do we map attributes?
- How do we map relationships between entities?
- Who manages the entities?

Hibernate implements JPA, we can think of JPA is an interface and Hibernate is a class that implements that interface.


## In Memory Database H2

In memory databases are created directly inside the application at run time. Once the application stops, the entire database including the tables and record are removed from memory, i.e. destroyed. The upside with this approach is that it doesn't require additional setup, hence it's easy to use for learning and unit tests.

```bash
# we can configure our application.properties file
spring.jpa.show-sql=true
spring.h2.console.enabled=true
```

We can check the data in the in-memory database.

- http://localhost:8080/h2-console
- jdbc:h2:mem:testdb

All of this magic is happening because we added the dependency to our pom.xml file and spring boot's auto-configuration kicked in.

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

## Best Practices

- Consumer first. The simpler it is for the end-user to understand our service, the better.
- Include high-quality documentation.
- Make the best user of HTTP, use the right request method and response status. e.g. return 400, Bad request instead of 500, server error.
- Don't leak secure information.
- Have a consistent approach of defining resources. e.g. /users, /users/{id}

https://www.springboottutorial.com/


