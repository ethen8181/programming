# sublime text
export PATH="$PATH:/Applications/Sublime Text.app/Contents/SharedSupport/bin"


# spark settings
export SPARK_HOME=~/spark
export PYSPARK_PYTHON=~/anaconda3/bin/python
# export PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
# export PACKAGES="com.databricks:spark-csv_2.11:1.4.0"
# export PYSPARK_SUBMIT_ARGS="--packages ${PACKAGES} pyspark-shell"


# appearance for the terminal
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi


# added by Anaconda3 installer
export PATH="~/anaconda3/bin:$PATH"


# enabling maven, remember to create .mavenrc file,
# to locate java home, we can use the command:
# /usr/libexec/java_home -v 1.8
# https://stackoverflow.com/questions/34563701/mvn-command-not-working-on-mac-os-x-yosmeti/34563765
# https://stackoverflow.com/questions/45230150/java-home-is-not-working-in-maven
export M2_HOME=/Users/mingyuliu/apache-maven-3.5.2
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$PATH:$JAVA_HOME/bin:$M2_HOME/bin


# hadoop
export HADOOP_HOME=~/hadoop-2.8.1
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
