# AI Agronomist - Autonomous Crop Inspection Drone

## Project Overview
This project is a **Closed-Loop Robotics System** that integrates **Machine Learning** with **ArduPilot** to perform autonomous crop health monitoring. Unlike standard drones that only collect data, this system analyzes sensor data in real-time and acts on it.

## Key Algorithms
1.  **Random Forest Classifier:** A trained ML model (`crop_health_model.pkl`) that predicts crop stress based on simulated Temperature and NDVI features.
2.  **Perlin Noise Simulation:** Generates realistic, spatially correlated vegetation patterns to test the drone's response.
3.  **Helix Inspection Maneuver:** A Dynamic Finite State Machine (FSM) that interrupts the mission to perform a 3D spiral scan when an anomaly is detected with >85% confidence.

## Tech Stack
* **Backend:** Python, Flask, DroneKit
* **Frontend:** HTML, JavaScript(Heat Map)
* **ML Engine:** Scikit-Learn, NumPy
* **Simulation:** ArduPilot SITL

## How to Run
1.  Start the Simulator: `sim_vehicle.py --map --console`
2.  Train the Brain: `python3 train_model.py`
3.  Start the Mission Control: `python3 app.py`
4.  Access Dashboard: `http://localhost:5000`
