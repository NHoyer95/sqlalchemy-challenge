# Import numpy and sqlalchemy dependencies
import numpy as np 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
# importing flask and jsonify for serve set up
from flask import Flask, jsonify

# Database set up
engine = create_engine("sqlite:///hawaii.sqlite")

base = automap_base()

base.prepare(engine, reflect=True)

measurement = base.classes.measurement
station = base.classes.station

# Setting up Flask
app = Flask(__name__)

# Creating the different flask routes
@app.route("/")
def welcome():
    """Return all of the available routes"""
    return(
        f"All of the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tempobservations<br/>"
        f"/api/v1.0/<start><br/>" 
        f"/api/v1.0/<start>/<end>"

    )

# return a jsonified dictionary of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():

    # variables needed
    recent_date = None
    last_year_precip = None

    # openning the session to pull queries in
    session = Session(engine)

    # finding the most recent date in data
    recent_date = session.query(measurement.date).order_by((measurement.date).\
        desc()).first()[0]
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    last_year_precip = session.query(measurement.date, measurement.prcp).order_by((measurement.date).asc()).\
        filter(measurement.date >= one_year_ago).filter(measurement.prcp).all()


    # closing the session once data is pulled
    session.close()
    
    # convert the query results into a dictionary
    precipitation_data = []
    for date, prcp in last_year_precip:
        temp_diction = {}
        temp_diction['date'] = date
        temp_diction['prcp'] = prcp
        precipitation_data.append(temp_diction)

    #return the jsonified dictionary
    return(jsonify(precipitation_data))

# return a jsonified list of stations from the data set
@app.route("/api/v1.0/stations")
def station():

    # open a session
    session = Session(engine)

    # query for a list of stations within the dataset
    stations_list = session.query(Station.station, Station.name).all()

    # closing the session
    session.close()

    # returning the jsonified list of stations and station names
    return(jsonify(stations_list))

@app.route("/api/v1.0/tempobservations")
def tobs():
    #open session to query from
    session = Session(engine)

    # finding the most recent date in data
    recent_date = session.query(measurement.date).order_by((measurement.date).\
        desc()).first()[0]
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the dates and tobs of the most active station for the last year
    most_active_station = session.query(measurement.station).order_by((measurement.date).asc()).\
        filter(measurement.date >= one_year_ago).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()[0][0]

    # getting precipitation data for most active station
    precip_data = session.query(measurement.tobs).filter(measurement.station == most_active_station).\
        order_by((measurement.date).asc()).filter(measurement.date >= one_year_ago).all()

    # Closing the session
    session.close()

    # return a JSON list of temperature observations (tobs) for the previous year
    return(jsonify(precip_data))

@app.route("/api/v1.0/<start>")
def start(start=None):
    #Opening the session 
    session = Session(engine)

    # Query for the min, max, and avg temperatures for all dates greater than and equal to start date
    start_date_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),
        func.max(measurement.tobs)).filter(measurement.date >= start).all()

    #closing the session
    session.close()

    #Returning the jsonified list of min, avg, max
    return(jsonify(start_date_query))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    #Opening the session 
    session = Session(engine)

    # Query for the min, max, and avg temperatures for all dates greater than and equal to start date
    # and less than and equal to the end date
    start_end_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    #closing the session
    session.close()

    #Returning the jsonified list of min, avg, max
    return(jsonify(start_end_query))


# End sequence for Flask
if __name__ == '__main__':
    app.run(debug=True)