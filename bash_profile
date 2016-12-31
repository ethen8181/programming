# sublime text
export PATH=$PATH:/Applications/Sublime\ Text\ 2.app/Contents/SharedSupport/bin

# ValueError: unknown locale: UTF-8 in Python
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8


export SPARK_HOME=~/spark
export PYSPARK_PYTHON=python3
export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
export PACKAGES="com.databricks:spark-csv_2.11:1.4.0"
export PYSPARK_SUBMIT_ARGS="--packages ${PACKAGES} pyspark-shell"


if [ -f ~/.bashrc ]; then
	source ~/.bashrc
fi

# added by Anaconda3 4.0.0 installer
export PATH="/Users/ethen/anaconda/bin:$PATH"
