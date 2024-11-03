from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/waypoint', methods=['POST'])
def waypoint():
    data = request.get_json()
    waypoints = data.get('waypoints', [])

    # Process each waypoint and perform actions
    for waypoint in waypoints:
        lat = waypoint.get('lat')
        lon = waypoint.get('lon')
        alt = waypoint.get('alt')
        action = waypoint.get('action')

        # Example: Print the waypoint details (you may implement your own logic)
        print(f"Waypoint - Lat: {lat}, Lon: {lon}, Alt: {alt}, Action: {action}")

    return jsonify({'message': 'Waypoints received successfully'}), 200

@app.route('/arm', methods=['POST'])
def arm():
    # Logic to arm the drone
    return jsonify({'message': 'Drone armed'}), 200

@app.route('/disarm', methods=['POST'])
def disarm():
    # Logic to disarm the drone
    return jsonify({'message': 'Drone disarmed'}), 200

@app.route('/takeoff', methods=['POST'])
def takeoff():
    data = request.get_json()
    altitude = data.get('altitude', 10)  # Default to 10 if not provided
    # Logic for drone takeoff
    return jsonify({'message': f'Drone taking off to {altitude} meters'}), 200

@app.route('/land', methods=['POST'])
def land():
    # Logic for drone landing
    return jsonify({'message': 'Drone landing'}), 200

if __name__ == '__main__':
    app.run(debug=True)
