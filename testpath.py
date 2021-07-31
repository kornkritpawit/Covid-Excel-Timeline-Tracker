from os.path import *
print(dirname(__file__))

# Os.path.abspath (__ file__) returns the absolute path (full path) .py file
path2=abspath(__file__)
print(path2)
 
 # Combination
path3=dirname(abspath(__file__))
print(path3)
 
 # join () stitching path
path4= join(dirname(abspath(__file__)),'1.py')
print(path4)

print(__file__)

path3=dirname(abspath(''))
print(path3)