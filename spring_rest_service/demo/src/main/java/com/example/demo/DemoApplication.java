package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;

@SpringBootApplication
public class DemoApplication {

	public static void main(String[] args) {
	    /*
	        Our sorting algorithm is a dependency for our binary search, so can
	        we take a step further and avoid this dependency? This is where spring
	        comes into the equation.

	        One of the most important concept for Spring is dependency injection and
	        loose coupling.

	        Terminology: Bean, an instance of the object. In our case, the QuickSortAlgorithm

	        We would like to create a bean and "wire" it to its dependencies. In our case,
	        the bean QuickSortAlgorithm is BinarySearchImpl's dependency.

	        Spring framework gives us the capability to achieve this. To leverage the framework,
	        we need to tell Spring
	        1. What are the beans
	        2. What are the dependencies of a bean?
	        3. Where to search for beans

	        - We define a bean using the Component annotation and a dependency using the Autowired annotation
	        - SpringBootApplication would scan the package and its sub-package where the main application class
	        is present
	     */

	    // after marking the bean with Spring's syntax, it would manage the creation of those beans with
        // application context
        // BinarySearchImpl search = new BinarySearchImpl(new QuickSortAlgorithm());
		// int result = search.binarySearch(new int[] {124, 6}, 3);

		ApplicationContext applicationContext = SpringApplication.run(DemoApplication.class, args);
        /*
            Spring auto-wire the binarySearchImpl and QuickSortAlgorithm together base on the annotation
            we've provided while creating the binarySearchImpl bean. Here we've only annotated the
            QuickSortAlgorithm. If we were to annotate both QuickSortAlgorithm, BubbleSortAlgorithm, then
            we can add the @Primary annotation to tell spring which one to use first.
         */
        BinarySearchImpl search1 = applicationContext.getBean(BinarySearchImpl.class);
        int result1 = search1.binarySearch(new int[] {124, 6}, 3);
        System.out.println(result1);

        // another way of doing autowiring to use setter injection, i.e. we define a setter instead of constructor
        // for BinarySearchImpl2's dependencies. Not defining the setter is also the same
        BinarySearchImpl2 search2 = applicationContext.getBean(BinarySearchImpl2.class);
        int result2 = search2.binarySearch(new int[] {124, 6}, 3);
        System.out.println(result2);
	}

}
