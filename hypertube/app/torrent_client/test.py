import subprocess
import sys
import os

argv1 = sys.argv

p1 = subprocess.run(["python3", "main.py", argv1[1]])

#print(p1.stdout.decode())