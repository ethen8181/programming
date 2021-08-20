
host=ec2-54-147-225-97.compute-1.amazonaws.com
scp -i ethen.pem -r /Users/mingyuliu/Desktop/avito ubuntu@${host}:~/.
host=ec2-54-147-225-97.compute-1.amazonaws.com
ssh -i ethen.pem ubuntu@${host}


sudo apt-get update
sudo apt-get install -y gcc g++ python-pip wget

# default installed location /home/ubuntu/anaconda3
# alternative, to install in silent mode
# https://conda.io/docs/user-guide/install/macos.html#installing-in-silent-mode
# change to installing miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source .bashrc

cd avito
conda create --name avito python=3.5
source activate avito
pip install -r requirements.txt

bash run_models.sh

# https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html
# aws s3 cp s3://ethen/avito . --recursive

# sudo apt install awscli
# sudo apt install pip

# AKIAJCETJ3SHNGFKZJTA
# d2VP1LOjx/jEOCim/r5qMSJgCzQW28ME7HJeS7nE
# us-east-1
# text
