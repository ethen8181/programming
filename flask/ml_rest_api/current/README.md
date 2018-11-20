# Flask REST API

To start with, we create a Flask application that returns a json payload saying hello world when calling the root endpoint.

We can test the Flask app using its built-in development server.

```bash
python app.py
```

After that we can use the following curl request to test the endpoint. `curl -X GET http://127.0.0.1:8080/`. If all things go well, we should see the json payload returned.


Testing gunicorn's ability to serve the project.

```bash
gunicorn --bind 127.0.0.1:8080 app:app
```


## Docker

```bash 
docker build --no-cache -t ml_rest_api .
docker run -t -p 8080:8080 ml_rest_api
```

After building the docker image and running the container. The endpoint should be callable. `curl -X GET http://127.0.0.1:8080/`

Notes regarding ports in Docker containers. Docker container can connect to the outside world without additional configurations, but by default the outside world can't connect to Docker containers.

We can specify which port from the container we wish to expose. This can be specified via the [`EXPOSE command`](https://docs.docker.com/engine/reference/builder/#expose). For example, in our Dockerfile, we specified a line `EXPOSE 8080`. This instruction doesn't actually publish the port, instead it serves as a documentation between the pseron who built the image the the person who runs the container about which ports are intended to be published. To actually publish the port, we can be the `-p` flag on the docker run command. In our case `-p 8080:8080` means bind the Docker host port 8080 (Docker host is a terminology that refers to the machine that the docker engine is installed and being used to run Docker), this is referring to the first number in front of : to the container port 8080.

By default, Docker exposes container ports to the IP address 0.0.0.0 (this matches any IP on the system). If we prefer, you can tell Docker which IP to bind on. To bind on IP address 10.0.0.3, host port 80, and container port 8080. `docker run -p 10.0.0.3:80:8080`

Some helpful docker commands

```bash
# listing docker images
docker images

# removing docker images
docker rmi [insert docker image id]

# list running containers
docker ps

# stopping containers
docker stop [container id]
```

## Nginx

- http://nginx.org/en/docs/beginners_guide.html

```bash
# Installing Nginx in Mac OS X Maverick With Homebrew
# https://medium.com/@ThomasTan/installing-nginx-in-mac-os-x-maverick-with-homebrew-d8867b7e8a5a
brew install nginx

# http://localhost:8080, we should see some sort of message welcome to nginx
nginx

# signal
nginx -s stop
```




The default port has been set in /usr/local/etc/nginx/nginx.conf to 8080 so that
nginx can run without sudo.

nginx will load all files in /usr/local/etc/nginx/servers/.

# Reference

- [Blog: Docker Binding Ports](https://runnable.com/docker/binding-docker-ports)