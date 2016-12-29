# import the necessary components for your Flask app
from flask import Flask, render_template
import os
import pandas as pd
# from apscheduler.schedulers.background import BackgroundScheduler # Note: pip install APScheduler; for autoscheduling
# from apscheduler.triggers.interval import IntervalTrigger # Note: pip install APScheduler; for autoscheduling
# from pydataset import data # Note: pip install pydataset; load lots of toy dataset examples

# initialization #
# create instance of Flask class
app = Flask(__name__)


# template routes #
# this is the route for our home page
@app.route('/')
def home():
    return render_template('index.html')


# retrieve data from the large file and write smaller files for individual analysis
def prep_data(filename, splitvar):
    # read in the csv file and convert it to a Pandas data frame
    data = pd.DataFrame(pd.read_csv('static/data/' + filename + '.csv'))
    # get list of categories
    categories = data[splitvar].unique()
    # create a data frame dictionary to store your data frames
    DataFrameDict = {elem: pd.DataFrame for elem in categories}
    for key in DataFrameDict.keys():
        # create an object for each key in your dictionary
        DataFrameDict[key] = data[:][data[splitvar] == key]
    # now we can do a lookup of our smaller dataframes
    for key in categories:
        df = DataFrameDict[key]
        df.to_csv('static/data/chunks/' + str(key) + '.csv')

# note that at the moment, we are just writing our new dataframes to a csv file for storage and retrieval by our route.
# this is far from ideal. you don't want to typically store data within the application itself, and instead should
# push data storage to a database such as MongoDB or SQL. I typically use MongoDB because it's easy and I like it.


prep_data('bankcase', 'STATE')


# the <groupname> is reflective of your route. You can direct to a specific file from a previous page by passing
# the file name through the URL. This is then picked up by your Python function, and used to display the data feed.
@app.route('/intro/<groupname>/')
def intro(groupname):
    # read in the csv file and convert it to a Pandas data frame
    # this is where you would instead read from a database, not a csv file
    data = pd.DataFrame(pd.read_csv('static/data/chunks/' + groupname + '.csv'))
    # convert to datetime and set as an index in the data frame
    # have you also noticed how I am setting an index in this route and doing some formatting?
    # it's likely that you would have to do this elsewhere, so it would probably be best to abstract this away
    # from this function and do some of this prep before placing your data in your database
    data.time = pd.to_datetime(data['CUST_OPN_DT'], format='%m/%d/%Y')
    data.set_index(['CUST_OPN_DT'])
    # return your template, along with the file name and table. .to_html() tells Flask to
    return render_template("intro.html", name=groupname, data=data.to_html())


# uncomment the section below to enable custom error templates, such as a 404 page
# @app.errorhandler(404)
# def page_not_found():
#     return render_template('404.html'), 404


# once the app is running, use a cron job to fire the data prep function every day. Note: pip install APScheduler
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=prep_data,
#     trigger=IntervalTrigger(days=1) # can also be minutes, hours, etc.
# )
# # shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())


# run your Flask app #
# if you plan on deploying your app on Heroku, the settings below are what you need
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
