# https://blog.keras.io/running-jupyter-notebooks-on-gpu-on-aws-a-starter-guide.html
# https://chrisalbon.com/software_engineering/cloud_computing/run_project_jupyter_on_amazon_ec2/

# installed location /home/ubuntu/anaconda3
wget https://repo.continuum.io/archive/Anaconda3-5.1.0-Linux-x86_64.sh
bash Anaconda3-5.1.0-Linux-x86_64.sh
source .bashrc

# set up SSL certificates
mkdir ssl
cd ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout "cert.key" -out "cert.pem" -batch
cd ..

# configure jupyter notebook
jupyter notebook --generate-config

ipython
from IPython.lib import passwd
passwd()
exit

vi ~/.jupyter/jupyter_notebook_config.py
c = get_config()  # get the config object
c.NotebookApp.certfile = u'/home/ubuntu/ssl/cert.pem' # path to the certificate we generated
c.NotebookApp.keyfile = u'/home/ubuntu/ssl/cert.key' # path to the certificate key we generated
c.IPKernelApp.pylab = 'inline'  # in-line figure when using Matplotlib
c.NotebookApp.ip = '*'  # serve the notebooks locally
c.NotebookApp.open_browser = False  # do not open a browser window by default when using notebooks
c.NotebookApp.password = u'fill with sha1 password'  # this is the password hash that we generated earlier.

sudo apt-get install -y gcc g++


# run notebook and scp results notebook back to local
scp -i ethen.pem -r aws ubuntu@ec2-18-218-86-43.us-east-2.compute.amazonaws.com:~/.

cd aws
python setup.py install

scp -i ethen.pem ubuntu@ec2-18-218-86-43.us-east-2.compute.amazonaws.com:~/aws/examples/benchmark_als.ipynb ./benchmark_als.ipynb