import os
import sys

print(os.path.dirname(__file__))

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(dir_path)
print(dir_path)

# from flask_script import Manager, Server
# from application import create_app

