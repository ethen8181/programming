#include <iostream>
#include <iterator>
#include <unordered_set>
#include <algorithm> // min

double apk(std::unordered_set<int> &actual, int y_pred[], int k) {

    int p = 0;
    double n_hit = 0;
    double precision = 0.0;
    for (int i = 0; i < k; i++) {
        p = y_pred[i];
        if (actual.find(p) != actual.end()) {
            n_hit += 1;
            precision += n_hit / (i + 1);
        }
    }

    int size = actual.size();
    double avg_precision = precision / std::min(size, k);
    return avg_precision;
}

int main() {

    int k = 2;
    int y_true[] = {1, 2, 3, 4, 5};
    int y_pred[] = {6, 4};
    
    // https://www.programiz.com/cpp-programming/passing-arrays-function
    // the argument marks in the code represents the memory address 
    // of first element of array; and in the function argument
    // the formal argument int arr[] declaration converts to int* m;. 
    // This pointer points to the memory address of the array; it is
    // handled this way to save memory and time

    // http://stackoverflow.com/questions/20598235/convert-array-to-set-in-c
    std::unordered_set<int> actual(std::begin(y_true), std::end(y_true));
    double avg_precision = apk(actual, y_pred, k);
    std::cout << avg_precision;

    // http://stackoverflow.com/questions/20598235/convert-array-to-set-in-c
    // std::unordered_set<int> actual(std::begin(y_true), std::end(y_true));

    // int p = 0;
    // double n_hit = 0;
    // double precision = 0.0
    // double avg_precision = 0.0;

    // int n = sizeof(y_pred) / sizeof(y_pred[0]);
    // std::cout << "n" << n << "\n";
    
    // for (int i = 0; i < n; i++) {
    //     p = y_pred[i];
    //     std::cout << p;
    //     if (actual.find(p) != actual.end()) {
    //         n_hit += 1;
    //         precision += n_hit / (i + 1);
    //     }
    // }
    
    // std::cout << "\n";

    // std::cout << "n_hit" << n_hit << "\n";


    // int size = actual.size();
    
    // std::cout << "precision" << precision << "\n";
    // std::cout << avg_precision << "\n";
    // double recall = std::min(size, k);
    // std::cout << "recall" << recall << "\n";
    // avg_precision = precision / recall;
    // std::cout << avg_precision;

    // std::unordered_set<int>::iterator itr;
    // for (itr = actual.begin(); itr != actual.end(); itr++) {
    //     std::cout << *itr << " ";
    // }

    return 0;
}



