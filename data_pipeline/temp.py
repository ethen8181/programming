# 1. when does this task begin? does it have a time limit?
# 2. what are the necessary inputs for this task?
# 3. what constitues success for this task?
# 4. if this task fails, what should happen?
# 5. what does the task produce? to whom? how?
# 6. what, if anything, should happen after this task concludes?

pip install celery
pip install pandas_datareader

# http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html
# The RabbitMQ server scripts are installed into /usr/local/sbin.
# This is not automatically added to our path, so we may wish to add
# the following command to our .bash_profile
brew install rabbitmq
export PATH=$PATH:/usr/local/sbin

# To use Celery we need to create a RabbitMQ user,
# a virtual host and allow that user access to that virtual host
# Substitute in appropriate values for myuser, mypassword and myvhost below
# http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html#setting-up-rabbitmq
rabbitmqctl add_user myuser mypassword
rabbitmqctl add_vhost myvhost
rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
