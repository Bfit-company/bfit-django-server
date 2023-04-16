docker build --tag python-django .
docker run -d --publish 8000:8000 python-django