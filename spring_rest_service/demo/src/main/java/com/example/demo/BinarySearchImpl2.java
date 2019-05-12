package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/*
    Sort the array, search the array, return the index of the match
 */
@Component
public class BinarySearchImpl2 {

    @Autowired
    private SortAlgorithm sortAlgorithm;

    public int binarySearch(int[] numbers, int numberToSearchFor) {
        int[] sortedNumbers = sortAlgorithm.sort(numbers);
        return 3;
    }

    public void setSortAlgorithm(SortAlgorithm sortAlgorithm) {
        this.sortAlgorithm = sortAlgorithm;
    }
}
