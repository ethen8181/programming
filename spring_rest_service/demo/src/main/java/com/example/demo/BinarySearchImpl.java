package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/*
    Sort the array, search the array, return the index of the match
 */
@Component
public class BinarySearchImpl {

    /*
        if we were to use a sorting algorithm in the binarySearch method,
        then our binarySearch method's logic is tightly coupled with the
        sorting logic we're implementing here. Tight Coupling is when
        we wish change the sorting algorithm, we would need to change
        the code for our binarySearch.

        One way to make the sorting algorithm loosely coupled is to
        create a interface for it and pass it in from the constructor.
     */
    @Autowired
    private SortAlgorithm sortAlgorithm;

    public BinarySearchImpl(SortAlgorithm sortAlgorithm) {
        this.sortAlgorithm = sortAlgorithm;
    }

    public int binarySearch(int[] numbers, int numberToSearchFor) {
        int[] sortedNumbers = sortAlgorithm.sort(numbers);
        return 3;
    }
}
