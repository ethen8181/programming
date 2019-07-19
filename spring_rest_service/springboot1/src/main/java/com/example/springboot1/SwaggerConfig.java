package com.example.springboot1;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.service.Contact;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/*
    EnableSwagger2 and Docket are boilerplate code for enabling swagger documentation for our REST API.

    The distinction between @Component and @Bean, two ways to generate bean is explained in the article.
    One is to create a class with a @Component annotation and the other is to create a method that return
    the bean and annotate it with @Bean (we'll also need to annotate the class the method resides with @Configuration).

    When running the Spring project, the ComponentScan will scan every class with @Component and every method
    with @Bean. Both will then be managed by Spring.

    - @Component is a class-level annotation that can be applied to any class to the application to make that bean
    a spring managed component.
    - @Bean is a method-level annotation that is used to register the bean returned by the method as a spring
    configuration bean in the IOC container. Annotating a class with the @Configuration annotation indicates that
    the class can be used by the Spring IOC container as a source of bean definitions. Then the @Bean annotation
    tells Spring that a method annotated with @Bean will return an object that should be registered as a bean
    in the Spring application context.

    https://stackoverflow.com/questions/10604298/spring-component-versus-bean
    https://www.tutorialspoint.com/spring/spring_bean_definition.htm
    https://www.tutorialspoint.com/spring/spring_java_based_configuration.htm
    https://www.journaldev.com/2623/spring-autowired-annotation#spring-autowired-annotation-and-qualifier-bean-autowiring-by-constructor-example
 */
@Configuration
@EnableSwagger2
public class SwaggerConfig {

    // we can customize the default swagger documentation to our likings
    private static final Contact
        DEFAULT_CONTACT = new Contact("", "", "");

    private static final ApiInfo
        DEFAULT_API_INFO = new ApiInfo(
            "Awesome Api Documentation", "Our Awesome Documentation Description",
            "1.0", "urn:tos", DEFAULT_CONTACT,
            "Apache 2.0", "http://www.apache.org/licenses/LICENSE-2.0", new ArrayList());

    private static final Set<String>
        DEFAULT_PRODUCES_AND_CONSUMES = new HashSet<>(Arrays.asList("application/json", "application/xml"));

    @Bean
    public Docket api() {
        return new Docket(DocumentationType.SWAGGER_2)
            .apiInfo(DEFAULT_API_INFO)
            .produces(DEFAULT_PRODUCES_AND_CONSUMES)
            .consumes(DEFAULT_PRODUCES_AND_CONSUMES);
    }
}
