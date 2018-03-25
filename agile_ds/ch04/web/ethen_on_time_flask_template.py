from pymongo import MongoClient
from elasticsearch import Elasticsearch
from flask import Flask, request, render_template


RECORDS_PER_PAGE = 20
ELASTIC_URL = "agile_data_science"

app = Flask(__name__)
client = MongoClient()
elastic = Elasticsearch()


@app.route("/on_time_performance")
def on_time_performance():
    """
    Display a flight by passing in Carrier, FlightDate and FlightNum.

    Examples
    --------
    http://127.0.0.1:5000/on_time_performance?Carrier=DL&FlightDate=2015-01-01&FlightNum=478
    """
    carrier = request.args.get('Carrier')
    flight_date = request.args.get('FlightDate')
    flight_num = request.args.get('FlightNum')

    flight = client.agile_data_science.on_time_performance.find_one({
        'Carrier': carrier,
        'FlightDate': flight_date,
        'FlightNum': flight_num
    })
    return render_template('ethen_flight.html', flight=flight)


@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
    """
    Fetch all flights between cities on a given day and display them.
    The display will be sorted by departure time and arrival time.

    Supports pagination, where the number of records per page is
    controlled by RECORDS_PER_PAGE

    Examples
    --------
    - http://127.0.0.1:5000/flights/ATL/SFO/2015-01-01
    - http://127.0.0.1:5000/flights/ORD/SFO/2015-01-01?start=40&end=60
    """
    start, end = get_pagination_params()
    nav_offsets = get_navigation_offsets(start, end, RECORDS_PER_PAGE)

    # sort both departure time and arrival time in ascending order,
    # please remember to create the index in mongodb, or else this
    # query will become very slow
    # db.on_time_performance.createIndex({Origin: 1, Dest: 1, FlightDate: 1})
    flights = client.agile_data_science.on_time_performance.find(
        {'Origin': origin, 'Dest': dest, 'FlightDate': flight_date},
        sort = [('DepTime', 1), ('ArrTime', 1)]
    ).skip(start).limit(RECORDS_PER_PAGE)
    flight_count = flights.count()

    return render_template(
        'ethen_flights.html', flights=flights, flight_date=flight_date,
        flight_count=flight_count, nav_offsets=nav_offsets, nav_path=request.path)


@app.route("/flights/search/")
@app.route("/flights/search")
def search_flights():
    """
    Search using input boxes:

    e.g.
    Origin : ORD
    Dest : SFO
    FlightDate : 2015-07-31

    Examples
    --------
    http://127.0.0.1:5000/flights/search?Carrier=&Origin=ORD&Dest=SFO&FlightDate=2015-07-31&TailNumber=&FlightNumber=
    """
    
    start, end = get_pagination_params()
    nav_offsets = get_navigation_offsets(start, end, RECORDS_PER_PAGE)

    # search parameters
    carrier = request.args.get('Carrier')
    flight_date = request.args.get('FlightDate')
    origin = request.args.get('Origin')
    dest = request.args.get('Dest')
    tail_number = request.args.get('TailNum')
    flight_number = request.args.get('FlightNum')

    # nav_path = parse_url(request.path)
    
    # build elasticsearch query 
    must_query = []
    if carrier:
        must_query.append({'match': {'Carrier': carrier}})
    if flight_date:
        must_query.append({'match': {'FlightDate': flight_date}})
    if origin:
        must_query.append({'match': {'Origin': origin}})
    if dest:
        must_query.append({'match': {'Dest': dest}})
    if tail_number:
        must_query.append({'match': {'TailNum': tail_number}})
    if flight_number:
        must_query.append({'match': {'FlightNum': flight_number}})
    
    query_body = {
        'query': {
            'bool': {
                'must': must_query
            }
        },
        'sort': [
            '_score'
        ],
        'from': start,
        'size': RECORDS_PER_PAGE
    }
    results = elastic.search(index=ELASTIC_URL, body=query_body)
    flights, flight_count = process_search(results)

    return render_template(
        'ethen_search.html', nav_path=request.path, nav_offsets=nav_offsets,
        carrier=carrier, flight_date=flight_date, origin=origin,
        dest=dest, tail_number=tail_number, flight_number=flight_number,
        flights=flights, flight_count=flight_count)


def process_search(results):
    """
    Return list of records and total number of records
    from an elasticsearch query result
    """
    records = []
    total_records = 0
    if results['hits']['hits']:
        hits = results['hits']
        total_records = hits['total']
        records = [hit['_source'] for hit in hits['hits']]

    return records, total_records


def get_pagination_params():
    """Get the start and end record number"""
    start = request.args.get('start') or 0
    start = int(start)
    end = request.args.get('end') or RECORDS_PER_PAGE
    end = int(end)
    return start, end


def get_navigation_offsets(start, end, increment):
    """
    Returns a dictionary of previous and next page's record range.

    e.g. given a increment of 20
    we would like the link parameter to be something like:
    Previous: ?start=0&end=20
    Next: ?start=40&end=60
    """
    offsets = {}
    offsets['Previous'] = {'start': max(start - increment, 0), 'end': max(end - increment, 0)}
    offsets['Next'] = {'start': start + increment, 'end': end + increment}
    return offsets


if __name__ == "__main__":
    app.run(debug=True)
