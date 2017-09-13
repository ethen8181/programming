// overloading operators example
//http://www.cplusplus.com/doc/tutorial/templates/
#include <iostream>
using namespace std;

class CVector {
    public:
        int x, y;
        
        CVector(int x = 0, int y = 0) {
            this->x = x;
            this->y = y;
        }
        
        /* 
        e.g. if we were to write
        CVector operator+( CVector param)
        by passing arguments by value, the function
        is force to make a copy of the argument passed
        to the function when it is called, thus to increase
        efficiency for parameters of large types, the parameter
        is made references using the &, then by qualifying them
        as const, the function is forbidden to modify the value
        of of 'param', but can still access their values as 
        references (note that there will be no difference in
        efficiency for most fundamental types)
        */
        CVector operator+(const CVector& param) {
            CVector temp;
            temp.x = x + param.x;
            temp.y = y + param.y;
            return temp;
        }
};


int main() {
    CVector foo(3, 1);
    CVector bar(1, 2);
    CVector result;
    result = foo + bar;
    cout << result.x << ',' << result.y << '\n';
    return 0;
}
