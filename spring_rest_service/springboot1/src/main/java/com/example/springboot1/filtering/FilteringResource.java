package com.example.springboot1.filtering;

import com.fasterxml.jackson.databind.ser.FilterProvider;
import com.fasterxml.jackson.databind.ser.impl.SimpleBeanPropertyFilter;
import com.fasterxml.jackson.databind.ser.impl.SimpleFilterProvider;
import org.springframework.http.converter.json.MappingJacksonValue;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;

/*
    Let's say in our bean, there are certain fields in which we don't want to return its value in the response.
    e.g. A User class that contains the field "password".

    To do so, we can add a JsonIgnore annotation to the field. Or if we prefer to annotate the class,
    we can use JsonIgnoreProperties annotation and pass in the values. Though JsonIgnore might be better
    since we wouldn't be hard-coding additional stuff in the JsonIgnoreProperties.

    The filtering method above is known as a static filter, to change it to dynamic filter, where we can
    customize what field to exclude in the response for different request, we can use MappingJacksonValue
    along with the JsonFilter annotation.
 */
@RestController
public class FilteringResource {

    @GetMapping("/filtering")
    public MappingJacksonValue retrieveSomeBean() {

        SomeBean someBean = new SomeBean("value1", "value2", "value3");
        MappingJacksonValue mapping = new MappingJacksonValue(someBean);

        // note that we'll need to add SomeBeanFilter as a JsonFilter annotation for the class
        SimpleBeanPropertyFilter beanFilter = SimpleBeanPropertyFilter.filterOutAllExcept("field1", "field2");
        FilterProvider filterProvider = new SimpleFilterProvider().addFilter("SomeBeanFilter", beanFilter);
        mapping.setFilters(filterProvider);
        return mapping;
        // return someBean;
    }

    @GetMapping("/filtering-list")
    public MappingJacksonValue retrieveListOfSomeBean() {
        List<SomeBean> someBeans = Arrays.asList(
            new SomeBean("value1", "value2", "value3"), new SomeBean("value21", "value22", "value32"));

        MappingJacksonValue mapping = new MappingJacksonValue(someBeans);
        SimpleBeanPropertyFilter beanFilter = SimpleBeanPropertyFilter.filterOutAllExcept("field1", "field2");
        FilterProvider filterProvider = new SimpleFilterProvider().addFilter("SomeBeanFilter", beanFilter);
        mapping.setFilters(filterProvider);
        return mapping;
        //return someBeans;
    }
}

