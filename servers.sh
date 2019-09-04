
## Steps to host on our own server

The downside of heroku is that we don't have full control over the server (the computer that is hosting our application), the way that it is served or even caching. Thus, if we wish to have control over these things to tune performance, and are willing to do some extra work than hosting the application on our own server may be the better options for us.


https://www.digitalocean.com/?refcode=d54c088544ed&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=CopyPaste


```bash
# install postgres and nginx
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install nginx
```

```bash
# we can create an additional user so we don't have to login via root user
adduser ethen

# after typing visudo create a new line for our newly added user
# and copy the root user line over
visudo

# then we change the ssh settings so we can ssh into the server as that user
# PermitRootLogin no
# AllowUsers ethen
vi /etc/ssh/sshd_config

# reload so the changes takes affect
service sshd reload
```

```bash
sudo -i -u postgres

# we will create a new postgres user with a password and a database
createuser ethen -P
createdb ethen  # dropdb to drop tables

# change the method from peer to md5 for local, so that we will still
# get prompted for a password (to be safe)
sudo vi /etc/postgresql/9.5/main/pg_hba.conf 

# we can go inside psql and check to make sure we're using the correct user
# and we're using the right database
psql
\conninfo
\q
exit
```

```bash
# enable ubuntu firewall
sudo ufw allow
sudo ufw allow 'Nginx HTTP'
sudo ufw allow ssh

# check to see if nginx is running
# systemctl [start/stop/restart] nginx
systemctl status nginx

sudo vi /etc/nginx/sites-available/items-rest.conf
```

The nginx's server will be able to listen to incoming requests and dispatch them whereever appropriate.

- The server will be listening to port 80, which the default http port. Whenever we access a webpage on the internet, we're actually accessing port 80. When using the default port, the end-user doesn't have to specify the port number.
- Forward the IP request to our application. i.e. nginx will tell us who made that request. When we're specifying where the actual nginx IP is, in our case, we're hosting in on local.
- location /, whenever someone accesses the root url of the server, we're going to redirect them to our application.
    - We need to add the `include uwsgi_params` to make sure nginx is able to communicate with uwsgi.
    - `uwsgi_pass`. nginx is going to pass to the specified file all the necessary parameters. The file is our connection point between our app and nginx. We of course also need to create that .sock file.
    - `uwsgi_modifier` A uwsgi parameter that tells the thread when to die when it becomes blocked.
- nginx has built-in web pages that we can redirect the end-users to. e.g. when we encounter an error specify the location to redirect them to.

```
server {
    listen 80;
    real_ip_header X-Forwarded-For;
    set_real_ip_from 127.0.0.1;
    server_name localhost;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/html/items-rest/socket.sock;
        uwsgi_modifier 30;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

```bash
# create a soft link between our configuration and the /sites-enabled folder where
# nginx will read its configurations
sudo ln -s /etc/nginx/sites-available/items-rest.conf /etc/nginx/sites-enabled/

# this is where our application is going to reside as specified in the config file
sudo mkdir /var/www/html/items-rest/

# since we created it as the root user, we need to make sure other users can access it
sudo chown ethen:ethen /var/www/html/items-rest/

cd /var/www/html/items-rest/

# libpq-dev is for postgresql
sudo apt-get install python3-pip python3-dev libpq-dev

# we can create a virtual environment if we don't wish to polluate the environment
# pip install virtualenv
# virtualenv venv --python=python3.5
# source venv/bin/activate
git clone https://github.com/ethen8181/stores-rest-flask.git .

mv stores-rest-flask/* .
rm -r stores-rest-flask
pip3 install -r requirements.txt

# create a log folder to store the logging
mkdir log
```

```bash
# we need to configure uwsgi so that our application and nginx
# can communicate with uwsgi 
```


```bash
# change from current user to root
sudo su
```


nginx is a reverse proxy, it acts as a gateway between our application and external users. It's going to
accept incoming request and decide what to do with them. In our case, we're going to configure them to go
straight to our application.

Having nginx will enable multi-threading for our app, it also allows us to run multiple applications
simultaneously within our server while redirecting different requests to different apps depending on some
parameters