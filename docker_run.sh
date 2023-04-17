docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi -f $(docker images -aq)
docker build --tag python-django .
docker run -d --publish 8000:8000 python-django