// classes example
// http://www.cplusplus.com/doc/tutorial/classes/
#include <iostream>
using namespace std;

class Rectangle {
    // members are private by default
    int width, height;
    
    public:
        // constructor
        Rectangle(int width = 5, int height = 5) {
            this->width = width;
            this->height = height;
        }
        
        int area() {
            return width * height;
        }
};


int main() {
    // define a object of the class and use the function
    // that is publicly accessible
    Rectangle rect1;
    Rectangle rect2(3, 4);
    cout << "area: " << rect1.area() << endl;
    cout << "area: " << rect2.area();
    return 0;
}