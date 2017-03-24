// destructors
#include <iostream>
#include <string>
using namespace std;

class Example4 {
    string* ptr;
    public:
        // constructors:
        Example4(const string& str) {
            // this is just an example of how to initialize string pointers
            // and using destructor to delete the manually allocated memory
            // but ideally we should just use something like string not_pointer_str = str
            // http://stackoverflow.com/questions/11859737/how-to-initialize-string-pointer
            ptr = new string(str);
        }
        
        // destructor:
        ~Example4() {
            delete ptr;
        }
        
        // access content:
        const string& content() {
            return *ptr;
        }
};

int main() {
    Example4 bar("Example");
    cout << "bar's content: " << bar.content() << '\n';
    return 0;
}


