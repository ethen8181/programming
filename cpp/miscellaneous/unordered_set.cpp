/*
 * unordered_set.cpp
 *
 *  Created on: Apr 17, 2017
 *      Author: ethen
 */

 // http://www.geeksforgeeks.org/unorderd_set-stl-uses/
#include <string>
#include <iostream>
#include <unordered_set>

void print_duplicate(int arr[], int length) {
    std::unordered_set<int> intSet;
    std::unordered_set<int> duplicate;

    for (int i = 0; i < length; i++) {
        if (intSet.find(arr[i]) == intSet.end()) {
            intSet.insert(arr[i]);
        } else {
            duplicate.insert(arr[i]);
        }
    }

    std::cout << "duplicated items are: ";
    std::unordered_set<int>::iterator itr;
    for (itr = duplicate.begin(); itr != duplicate.end(); itr++) {
        std::cout << *itr << " ";
    }
}

int main() {
    // in case unordered set is not found in eclipse
    // http://stackoverflow.com/questions/17131744/eclipse-cdt-indexer-does-not-know-c11-containers
    std::unordered_set<std::string> stringSet;
    // inserting various string, same string will be stored
    // once in set
    stringSet.insert("code");
    stringSet.insert("in");
    stringSet.insert("c++");
    stringSet.insert("is");
    stringSet.insert("fast");

    std::string key = "slow";

    //  find returns end iterator if key is not found,
    //  else it returns iterator to that key
    if (stringSet.find(key) == stringSet.end())
        std::cout << key << " not found\n\n";
    else
        std::cout << "Found " << key << std::endl << std::endl;

    key = "c++";
    if (stringSet.find(key) == stringSet.end())
        std::cout << key << " not found\n";
    else
        std::cout << "Found " << key << std::endl;

    // now iterating over whole set and printing its content
    std::cout << "\nAll elements : ";
    std::unordered_set<std::string>::iterator itr;
    for (itr = stringSet.begin(); itr != stringSet.end(); itr++) {
        std::cout << (*itr) << std::endl;
    }

    std::cout << "\n";
    int arr[] = {1, 5, 2, 1, 4, 3, 1, 7, 2, 8, 9, 5};
    int n = sizeof(arr) / sizeof(arr[0]);
    print_duplicate(arr, n);
    return 0;
}











