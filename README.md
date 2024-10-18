# Cookbook

## Installing this Package
Build Docker Image 
* `docker build .  && docker-compose build`

Update migration file 
* `docker-compose run --rm app /bin/sh -c "python manage.py makemigrations"`
* `docker-compose run --rm app /bin/sh -c "python manage.py migrate"`

Run Tests
* `docker-compose run --rm app /bin/sh -c 'python manage.py test'`

Run Application
* `docker-compose up`
