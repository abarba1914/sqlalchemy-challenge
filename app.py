import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"Preceiptation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Temp stats from start date: /api/v1.0/<start><br/>"
        f"Temp stats from start to end date: /api/v1.0/<start>/<end>"
    )

@app.route('/api/v1.0/precipitation')
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tempObs():
    session = Session(engine)

    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    dateOnly = dt.datetime.strptime(lastDate, '%Y-%m-%d')
    querydate = dateOnly- dt.timedelta(days=365)
    sel_query = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel_query).filter(Measurement.date >= querydate).all()
    session.close()

    tob_list = list(np.ravel(queryresult))

    return jsonify(tob_list)

@app.route('/api/v1.0/<start>')
def tempStats(start):
    session = Session(engine)

    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temp_list = list(np.ravel(stats))

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>/<end>')
def moreTemp(start,end):
    session = Session(engine)

    lastTemps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>= start).filter(Measurement.date<=end).all()
    session.close()

    temp_stats = list(np.ravel(lastTemps))

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)