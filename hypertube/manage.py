#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

#connect to server and create db

import mysql.connector as mysql

db = mysql.connect(
    host = '127.0.0.1',
    user = 'root',
    passwd = ''
)

if(db):
    print('connected successful....')
else:
    print('Try again please+++++++++')

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS hypertube")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypertube.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()