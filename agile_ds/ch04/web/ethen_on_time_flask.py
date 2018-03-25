from flask import Flask, request
from pymongo import MongoClient
from bson import json_util


# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()


@app.route("/on_time_performance")
def on_time_performance():
    """
    Example usage

    http://127.0.0.1:5000/on_time_performance?Carrier=DL&FlightDate=2015-01-01&FlightNum=478
    """

    # https://stackoverflow.com/questions/24892035/python-flask-how-to-get-parameters-from-a-url
    carrier = request.args.get('Carrier')
    flight_date = request.args.get('FlightDate')
    flight_num = request.args.get('FlightNum')

    flight = client.agile_data_science.on_time_performance.find_one({
        'Carrier': carrier,
        'FlightDate': flight_date,
        'FlightNum': flight_num
    })
    return json_util.dumps(flight)


if __name__ == "__main__":
    app.run(debug=True)