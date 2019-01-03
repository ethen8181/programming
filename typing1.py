"""
# We can introduce optional typing to our python code to enhance readability,
# and use mypy on our program to catch potential errors without actually running it.
# The following code is based on the series of excellent blog post by daftcode.

pip install mypy
mypy typing1.py

References
----------
- https://blog.daftcode.pl/first-steps-with-python-type-system-30e4296722af
- https://blog.daftcode.pl/next-steps-with-python-type-system-efc4df5251c9
- https://blog.daftcode.pl/csi-python-type-system-episode-1-1c2ee1f8047c
- https://mypy.readthedocs.io/en/latest/getting_started.html
"""



# ------------------------------------------------------------------------------
def add_ints(x: int, y: int) -> int:
    """We can annotate types of function's arugment and its return value"""
    return x + y


add_ints(1, 2)  
# add_ints(1, 2.0)  # mypy error


# ------------------------------------------------------------------------------
# list, List[Type of Elements]
from typing import List

my_list: List[int] = [1, 2, 3]

class Cat: pass

cat1 = Cat()
cat2 = Cat()

my_cats: List[Cat] = [cat1, cat2]


# ------------------------------------------------------------------------------
# tuple, Tuple[Type1, Type2]
from typing import Tuple

bob: Tuple[str, str, int] = ('Bob', 'Smith', 25)


# ------------------------------------------------------------------------------
# dictionary, Dict[KeyType, ValueType]
from typing import Dict

id_to_name: Dict[int, str] = {1: 'Bob', 23: 'Ann', 7: 'Kate'}


# ------------------------------------------------------------------------------
# union, Union[Type1, Type2, Type3]. Variable can accept multiple types
from typing import Union

width1: Union[int, float] = 20
width2: Union[int, float] = 20.5


# ------------------------------------------------------------------------------
# None, we can use Optional[int] to express Union[int, None]
from typing import Optional

def get_user_id() -> Optional[int]:
    temp = {'1': 1, '2': 2}  # mimicking some logic to return user_id
    return temp.get('1', None)

def process_user(user_id: int):
    pass


user_id = get_user_id()

# adding the is not None ensures that user_id will be of type int,
# which the process_user function expects
if user_id is not None:
    process_user(user_id)


# ------------------------------------------------------------------------------
# defining type alias by assigning type to a variable
from typing import Tuple

# create business logic types
# and annotate our code with these types
Item = Tuple[int, str, str]

def create_item() -> Item:
    pass


# ------------------------------------------------------------------------------
# in Python, functions are first class objects, meaning we can pass function itself
# into another function. Callable[[t1, t2, ..., tn], tr], defines a function with
# positional argument types t1, t2, ..., tn and has a return type of tr
from typing import Callable

def apply_function_on_value(func: Callable[[str], int], value: str) -> int:
    return func(value)


def text_length(text: str) -> int:
    return len(text)


result1 = apply_function_on_value(text_length, "i love apple")


# ------------------------------------------------------------------------------
from typing import Callable
# <: means is a subtype of, so B <: A reads "B is a subtype of A"
# a subtype is considered a less general type.

# e.g. Dog <: Animal means that
# 1. The set of values becomes smaller in the process of subtyping. Every Dog is an
# Animal, but not every Animal is a Dog, this means there are fewer Dogs than Animals.
# 2. The set of functions becomes larger. Functions of Animals (function of type A means
# function accepting object of type A as its argument, either it is a stand-alone function
# with a parameter of type A or a method defined on class A) contains a subset of Dog's
# function. Since Dog can do whatever Animal can, but Animal can't do everything a Dog can.

# So given, SubType <: SuperType, the assignment rule tells us the following
# variable assigment is valid.

# supertype_variable: SuperType (e.g. Animal)
# subtype_variable: SubType (e.g. Dog)
# supertype_variable = subtype_variable

# however, in the case of function's argument, subtyping works the other way around
# compared to plain objects. i.e. function with more general argument type is a
# subtype of function with less general argument type b

class Animal: pass

class Dog(Animal): pass

def animal_run(animal: Animal) -> None:
    print('An animal is running')

def dog_run(dog: Dog) -> None:
    print('A dog is running')

def make_dog_run(a_dog: Dog, run_func: Callable[[Dog], None]) -> None:
    run_func(a_dog)

# here, we can see that Callable[[Animal], None] <: Callable[[Dog], None]
# because a dog can run like a dog or an animal, but not the other way around
lassie = Dog()
make_dog_run(lassie, dog_run)
make_dog_run(lassie, animal_run)  # this part is valid
