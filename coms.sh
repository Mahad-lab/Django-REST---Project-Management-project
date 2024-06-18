#!/bin/bash

# Check if command parameter is provided
if [ -z "$1" ]; then
    echo "Please provide a command to run. Options are: start, makemigrations, migrate, test."
    exit 1
fi

command=$1

case $command in
    start)
        echo "Starting the Django server..."
        python manage.py runserver
        ;;
    makemigrations)
        echo "Making migrations..."
        python manage.py makemigrations
        ;;
    migrate)
        echo "Applying migrations..."
        python manage.py migrate
        ;;
    test)
        echo "Running tests..."
        python manage.py test
        ;;
    *)
        echo "Invalid command. Options are: start, makemigrations, migrate, test."
        exit 1
        ;;
esac