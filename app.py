import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
from flask import Flask, render_template, jsonify
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import threading
import math
import noise 
import numpy as np
import joblib 
import os

app = Flask(__name__)

MISSION_STATE = 0 
vehicle = None
ai_model = None

if os.path.exists('crop_health_model.pkl'):
    try:
        ai_model = joblib.load('crop_health_model.pkl')
        print("AI Model Loaded Successfully")
    except:
        print("Model Load Failed. Continuing without AI.")
else:
    print("Model missing. Run train_model.py first!")

def connect_drone():
    global vehicle
    if vehicle is None:
        try:
            print("Attempting to Connect to Drone...")
            vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
            print("Drone Connected!")
        except Exception as e:
            print(f"Connection Failed: {e}")

def get_sensor_data(lat_off, lon_off):
    scale = 100.0 
    noise_val = noise.pnoise2(lat_off*scale, lon_off*scale, octaves=6)
    
    ndvi = np.interp(noise_val, [-0.5, 0.5], [0.1, 0.9])
    temp = np.interp(noise_val, [-0.5, 0.5], [38, 22])
    
    confidence = 0
    if ai_model:
        try:
            probs = ai_model.predict_proba([[temp, ndvi*100]])
            confidence = max(probs[0]) * 100
        except:
            confidence = 85.0 

    status = "HEALTHY"
    if ndvi < 0.4:
        status = "STRESSED"
        
    return {"temp": round(temp, 1), "ndvi": round(ndvi, 2), "status": status, "conf": round(confidence, 1)}

def perform_helix_inspection(center_loc):
    global vehicle, MISSION_STATE
    print("ANOMALY FOUND - STARTING HELIX...")
    MISSION_STATE = 2 
    
    radius = 2.0
    alt = 10.0
    for i in range(3):
        angle = math.radians(i * 120)
        off_x = radius * math.cos(angle)
        off_y = radius * math.sin(angle)
        target = LocationGlobalRelative(center_loc.lat + (off_x/111111), center_loc.lon + (off_y/111111), alt - (i*1.5))
        vehicle.simple_goto(target)
        time.sleep(6)
        
    vehicle.simple_goto(LocationGlobalRelative(center_loc.lat, center_loc.lon, 10))
    time.sleep(5)
    MISSION_STATE = 1 

def mission_thread():
    global vehicle, MISSION_STATE
    print("Mission Started")
    MISSION_STATE = 1
    current_loc = vehicle.location.global_relative_frame
    waypoints = [(5,0), (10,0), (15,0), (15,5), (10,5), (5,5)]
    
    for wp in waypoints:
        lat_off = wp[0] * 0.00001
        lon_off = wp[1] * 0.00001
        data = get_sensor_data(lat_off, lon_off)
        
        if data['status'] == "STRESSED":
            target_spot = LocationGlobalRelative(current_loc.lat + lat_off, current_loc.lon + lon_off, 10)
            perform_helix_inspection(target_spot)
        
        target = LocationGlobalRelative(current_loc.lat + (wp[0]/111111), current_loc.lon + (wp[1]/111111), 10)
        vehicle.simple_goto(target)
        time.sleep(6)
        
    MISSION_STATE = 0
    print("Mission Complete")

@app.route('/')
def index():
    connect_drone() 
    return render_template('index.html')

@app.route('/takeoff')
def takeoff():
    global vehicle
    if vehicle is None:
        connect_drone()
    
    if vehicle:
        vehicle.parameters['ARMING_CHECK'] = 0 
        time.sleep(1)
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        while not vehicle.armed: time.sleep(1)
        vehicle.simple_takeoff(10)
        return jsonify({"message": "Launching Drone!"})
    else:
        return jsonify({"message": "Connection Failed. Is the Simulator Running?"})

@app.route('/fly_mission')
def fly_mission():
    global vehicle
    if vehicle:
        t = threading.Thread(target=mission_thread)
        t.start()
        return jsonify({"message": "Adaptive Mission Started!"})
    return jsonify({"message": "Connect Drone First"})

@app.route('/telemetry')
def telemetry():
    global vehicle
    if vehicle:
        start_lat = -35.363261
        start_lon = 149.165230
        curr_lat = vehicle.location.global_relative_frame.lat
        curr_lon = vehicle.location.global_relative_frame.lon
        
        lat_off = (curr_lat - start_lat) * 10000
        lon_off = (curr_lon - start_lon) * 10000
        
        data = get_sensor_data(lat_off, lon_off)
        
        return jsonify({
            "alt": round(vehicle.location.global_relative_frame.alt, 2),
            "lat": curr_lat - start_lat, 
            "lon": curr_lon - start_lon,
            "ndvi": data['ndvi'],     
            "temp": data['temp'],     
            "status": data['status'], 
            "state": MISSION_STATE
        })
    return jsonify({"alt": 0, "ndvi": 0, "temp": 0, "status": "--", "state": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
