import time
import firebase_admin
from firebase_admin import credentials, db
from dronekit import LocationGlobalRelative, connect, VehicleMode
from geopy.distance import geodesic

class DroneControl:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.vehicle = None

    def connect_drone(self):
        try:
            print("Connecting to vehicle on: %s" % self.connection_string)
            self.vehicle = connect(self.connection_string, baud=57600, wait_ready=True)
        except Exception as e:
            print(f"Error connecting to the drone: {e}")

    def arm_and_takeoff(self, target_altitude):
        try:
            print("Arming motors")
            self.vehicle.mode = VehicleMode("GUIDED")
            self.vehicle.armed = True
            
            while not self.vehicle.armed:
                print(" Waiting for arming...")
                time.sleep(1)

            print("Taking off!")
            self.vehicle.simple_takeoff(target_altitude)
            while True:
                print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
                if self.vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
                    print("Reached target altitude")
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error during arm and takeoff: {e}")

    def disarm_drone(self):
        try:
            if self.vehicle.armed:
                print("Disarming drone")
                self.vehicle.armed = False
                while self.vehicle.armed:
                    print(" Waiting for disarming...")
                    time.sleep(1)
                print("Drone disarmed successfully")
            else:
                print("Drone is already disarmed")
        except Exception as e:
            print(f"Error disarming the drone: {e}")

    def navigate_to_waypoint(self, lat, lon, alt):
        try:
            point = LocationGlobalRelative(lat, lon, alt)
            print(f"Going to waypoint: {point}")
            self.vehicle.simple_goto(point, airspeed=2)

            while True:
                current_location = self.vehicle.location.global_relative_frame
                distance = geodesic((current_location.lat, current_location.lon), (lat, lon)).meters
                print("Distance to waypoint: {}".format(distance))
                if distance < 1:
                    print("Reached waypoint")
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error navigating to waypoint: {e}")

    def perform_action(self, action):
        try:
            if action == 'Loiter':
                print("Performing Loiter action")
                self.vehicle.mode = VehicleMode("LOITER")
            elif action == 'Land':
                print("Performing Land action")
                self.vehicle.mode = VehicleMode("LAND")
            elif action == 'RTL':
                print("Performing RTL action")
                self.vehicle.mode = VehicleMode("RTL")
            else:
                print(f"Unknown action: {action}")
        except Exception as e:
            print(f"Error performing action {action}: {e}")

    def wait_at_waypoint(self, duration):
        try:
            print(f"Waiting at waypoint for {duration} seconds...")
            time.sleep(duration)
        except Exception as e:
            print(f"Error during wait at waypoint: {e}")

    def return_to_launch(self):
        try:
            print("Returning to Launch")
            self.vehicle.mode = VehicleMode("RTL")
        except Exception as e:
            print(f"Error returning to launch: {e}")

    def close_connection(self):
        if self.vehicle:
            print("Close vehicle object")
            self.vehicle.close()

    def listen_to_firebase(self):
        # Firebase Admin SDK initialization
        cred = credentials.Certificate("path/to/your/serviceAccountKey.json")  # Update the path
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://your-database-name.firebaseio.com/'  # Update with your database URL
        })

        # Define the database reference
        ref = db.reference('drone')

        # Continuously listen for changes
        while True:
            try:
                # Fetch the current state from Firebase
                state = ref.get()

                # Check for commands and act accordingly
                if state:
                    # Handle ARM command
                    if state.get('_arm') == '1111':
                        self.arm_and_takeoff(10)  # You can adjust this to fetch altitude from Firebase
                        ref.update({'_arm': '0000'})  # Reset the arm command

                    # Handle DISARM command
                    elif state.get('_disarm') == '0000':
                        self.disarm_drone()
                        ref.update({'_disarm': '0000'})  # Reset the disarm command

                    # Handle LAND command
                    elif state.get('_landed') == '1010':
                        print("Landing drone")
                        self.vehicle.mode = VehicleMode("LAND")
                        ref.update({'_landed': '0000'})  # Reset the land command

                    # Handle TAKEOFF command
                    elif state.get('_takeoff', '').startswith('0101'):
                        altitude = int(state['_takeoff'][4:])  # Fetch altitude from the command
                        self.arm_and_takeoff(altitude)
                        ref.update({'_takeoff': '0000'})  # Reset the takeoff command

                    # Handle automated waypoint navigation
                    elif state.get('_automatedpath') == '1100':
                        waypoints = state.get('waypoints', {})  # Get waypoints from Firebase
                        for wp in waypoints.values():
                            lat = wp.get('latitude')
                            lon = wp.get('longitude')
                            alt = wp.get('altitude')
                            action = wp.get('action', None)

                            if lat is not None and lon is not None and alt is not None:
                                self.navigate_to_waypoint(lat, lon, alt)
                                self.wait_at_waypoint(5)  # Wait at each waypoint for 5 seconds

                                if action:
                                    self.perform_action(action)  # Perform action specified at the waypoint
                            else:
                                print("Invalid waypoint data. Skipping...")
                        ref.update({'_automatedpath': '0000'})  # Reset automated path command

                # Update GPS location and speed to Firebase
                self.update_location_and_speed(ref)

                time.sleep(1)  # Polling interval
            except Exception as e:
                print(f"Error in Firebase listening loop: {e}")
                time.sleep(5)  # Wait before retrying on error

    def update_location_and_speed(self, ref):
        try:
            current_location = self.vehicle.location.global_frame
            speed = self.vehicle.groundspeed  # Speed in m/s

            # Prepare data to be updated in Firebase
            data = {
                'latitude': current_location.lat,
                'longitude': current_location.lon,
                'altitude': current_location.alt,
                'speed': speed
            }

            # Update the Firebase database
            ref.child('current_status').set(data)
            print(f"Updated location and speed to Firebase: {data}")
        except Exception as e:
            print(f"Error updating location and speed: {e}")

if __name__ == '__main__':
    connection_string = '/dev/ttyACM0'  # Replace with your connection string
    drone_control = DroneControl(connection_string)

    drone_control.connect_drone()
    drone_control.listen_to_firebase()  # Start listening for Firebase updates
