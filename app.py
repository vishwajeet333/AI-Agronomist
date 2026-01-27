import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
from flask import Flask, render_template, jsonify
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import threading

app = Flask(__name__)

# --- DRONE CONNECTION ---
vehicle = None

def connect_drone():
    global vehicle
    if vehicle is None:
        try:
            print("Connecting to Drone...")
            vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
            print("Drone Connected!")
        except Exception as e:
            print(f"Connection Failed: {e}")

# --- MISSION LOGIC ---
def mission_thread():
    global vehicle
    print("Starting Square Mission...")
    size = 10 
    
    current_loc = vehicle.location.global_relative_frame
    # NORTH
    print("oving NORTH")
    target = LocationGlobalRelative(current_loc.lat + (size/111111), current_loc.lon, 10)
    vehicle.simple_goto(target)
    time.sleep(10)

    # EAST
    print("oving EAST")
    target = LocationGlobalRelative(current_loc.lat + (size/111111), current_loc.lon + (size/111111), 10)
    vehicle.simple_goto(target)
    time.sleep(10)

    # SOUTH
    print("Moving SOUTH")
    target = LocationGlobalRelative(current_loc.lat, current_loc.lon + (size/111111), 10)
    vehicle.simple_goto(target)
    time.sleep(10)

    # WEST (Home)
    print("oving WEST")
    target = LocationGlobalRelative(current_loc.lat, current_loc.lon, 10)
    vehicle.simple_goto(target)
    time.sleep(10)
    print("Mission Complete")

# --- ROUTES ---
@app.route('/')
def index():
    connect_drone()
    return render_template('index.html')

@app.route('/takeoff')
def takeoff():
    global vehicle
    if vehicle:
        print("TAKEOFF COMMAND")
        vehicle.parameters['ARMING_CHECK'] = 0 # Disable Safety
        time.sleep(1)
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        while not vehicle.armed:
            time.sleep(1)
        vehicle.simple_takeoff(10)
        return jsonify({"status": "success", "message": "Taking Off!"})
    return jsonify({"status": "error", "message": "Not Connected"})

@app.route('/fly_square')
def fly_square():
    global vehicle
    if vehicle:
        t = threading.Thread(target=mission_thread)
        t.start()
        return jsonify({"status": "success", "message": "Square Mission Started!"})
    return jsonify({"status": "error", "message": "Not Connected"})

@app.route('/telemetry')
def telemetry():
    global vehicle
    if vehicle:
        return jsonify({
            "alt": round(vehicle.location.global_relative_frame.alt, 2),
            "mode": vehicle.mode.name,
            "lat": round(vehicle.location.global_relative_frame.lat, 6),
            "lon": round(vehicle.location.global_relative_frame.lon, 6)
        })
    return jsonify({"alt": 0, "mode": "DISCONNECTED", "lat": 0, "lon": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
