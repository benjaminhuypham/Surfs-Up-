import numpy as np
import pandas as pd 
import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement 
Station = Base.classes.station 

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return f"Welcome to Surfers!"

@app.route("/api/v1.0/precipitation")
def precipitation():
    lastDay = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastYear = dt.date(2017,8,23) - dt.timedelta(days=365)
    prcp_values = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= lastYear).order_by(Measurement.date).all()
    prcp_list = []
    for prcp in prcp_values:
        prcp_list.append(prcp_values[0])
        prcp_list.append(prcp_values[1])
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.name, Station.station)
    stations_df = pd.read_sql(stations.statement, stations.session.bind)
    return jsonify(stations_df.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    lastYear = dt.date(2017,8,23) - dt.timedelta(days=365)
    temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > lastYear).\
        order_by(Measurement.date).all()

    temp_list = []
    for temp in temps:
        temp_list.append(temps[0])
        temp_list.append(temps[1])
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start><end>")

def calc_temps_1(start, end):
    
    if not end:
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        temp_list = list(np.ravel(temps))
        return jsonify(temp_list)
        
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_list = list(np.ravel(temps))
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)

