# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Avaialble routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date)<br/>"
        f"/api/v1.0/(start_date/end_date)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent_date)
    twelve_months_ago = most_recent_date - pd.DateOffset(months=12)
    twelve_months_ago = twelve_months_ago.to_pydatetime()
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).all()
    session.close()
    
    results = list(np.ravel(results))
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station).all()
    session.close()
    
    stations = list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def most_active_station():
    most_active_station_id = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent_date)
    twelve_months_ago = most_recent_date - pd.DateOffset(months=12)
    twelve_months_ago = twelve_months_ago.to_pydatetime()
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station_id, measurement.date >= twelve_months_ago).all()
    session.close()
    
    results = list(np.ravel(results))
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start_date(start):
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start).all()
    lowest_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).scalar()
    highest_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).scalar()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).scalar()
    return jsonify (f"Lowest Temp: {lowest_temp}, Highest Temp: {highest_temp}, Avg Temp: {avg_temp}")
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start, measurement.date <= end).all()
    lowest_temp = session.query(func.min(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).scalar()
    highest_temp = session.query(func.max(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).scalar()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).scalar()
    return jsonify (f"Lowest Temp: {lowest_temp}, Highest Temp: {highest_temp}, Avg Temp: {avg_temp}")
    

if __name__ == "__main__":
    app.run(debug=True)