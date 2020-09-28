import sys
import os

a1 = sys.argv

with open(a1[1], 'r') as file:
    print(file.read())
    print(a1[1])