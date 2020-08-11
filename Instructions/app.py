#import all necessary directories
from flask import Flask, jsonify
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

#establish engine 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

#homepage 
#list all routes that are available
@app.route("/")
def homepage():
    """List all API routes"""
    return(
        f"Welcome to the Climate App!<br/>"
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temperature from start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature from start to end: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

#convert query results to a dictionary using date as the key and prcp as the value 
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    cols = [Measurement.date,Measurement.prcp]
    
    #select date and prcp columns
    result = session.query(*cols).all()
    session.close()

    #instantiate precipitation table
    precip = []
    for d,p in result:
        p_dict = {}
        p_dict["Date"] = d
        p_dict["Precipitation"] = p
        
        #add each element to the list 
        precip.append(p_dict)

    #return the JSON representation of your dictionary
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    cols = [Station.station]
    result = session.query(*cols).all()
    session.close()

    #instantiating stations list
    stations = []
    for s in result:
        s_list = {}
        s_list["Station"] = s

        #adding each element to the list 
        stations.append(s_list)

    #return a JSON list of temperature observations (TOBS) for the previous year 
    return jsonify(stations)

#query the dates and temperature observations of the most activve station for the last year of data
#return a JSON list of temperature observations (TOBS) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    date = dt.datetime.strptime(last[0], '%Y-%m-%d') - dt.timedelta(days = 365)
    
    result = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= date).\
        order_by(Measurement.date).all()
    
    list = []
    for d, t in result:
        dict = {}
        dict[d] = t
        list.append(dict)

    session.close()

    return jsonify(list)

#return a JSON list of the minimum temperature, average, and the max temperature for a given start or start-end range
@app.route("/api/v1.0/<start>")
def startRange(start):
    session = Session(engine)

    #select tobs column and find min, max and average 
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\

        #filtering the dates after the given start date
        filter(Measurement.date>=start).all()
    session.close()

    table = []
    for min,max,avg in result:
        dict = {}
        dict["min"] = min
        dict["max"] = max
        dict["average"] = avg
        table.append(dict)
    return jsonify(table)

@app.route("/api/v1.0/<start>/<end>")
def startStop(start,end):
    session = Session(engine)

    #select the tobs column and find the min, max and average
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        
        #filter by the dates after the given start date to the dates before the given end date
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    table = []
    for min,max,avg in result:
        dict = {}
        dict["min"] = min
        dict["max"] = max
        dict["average"] = avg
        table.append(dict)
    return jsonify(table)


if (__name__ == '__main__'):
    app.run(debug=True)