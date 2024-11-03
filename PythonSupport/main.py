from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QFormLayout, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys
import time
from dronekit import LocationGlobalRelative, connect, VehicleMode
from geopy.distance import geodesic

class DroneControlUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Drone Control UI')
        self.setGeometry(100, 100, 800, 600)

        # Set a modern and attractive color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)

        self.num_waypoints_input = QLineEdit(self)
        self.latitude_inputs = []
        self.longitude_inputs = []
        self.altitude_inputs = []
        self.action_comboboxes = []
        self.duration_inputs = []  
        self.add_waypoint_button = QPushButton('Add Waypoint', self)
        self.start_button = QPushButton('Start Drone Control', self)

        self.init_ui()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        form_layout = QFormLayout()
        form_layout.addRow(QLabel('Number of Waypoints:'), self.num_waypoints_input)

        main_layout.addLayout(form_layout)

        self.add_waypoint_button.clicked.connect(self.create_input_fields)

        for button in [self.add_waypoint_button]:
            main_layout.addWidget(button)

        main_layout.addLayout(self.create_input_fields_layout())

        scroll_area.setWidget(widget)

        main_layout = QVBoxLayout(self)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.start_button, alignment=Qt.AlignBottom)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(bottom_layout)

        self.start_button.clicked.connect(self.start_drone_control)

        self.setStyleSheet("""
            QLineEdit, QPushButton {
                font-size: 14px;
                padding: 8px;
                margin: 4px;
                border: 2px solid #e83f3f;
                border-radius: 5px;
                color: white;
                background-color: #282c35;
            }
            QPushButton {
                background-color: #4CAF50;
            }
            QPushButton:hover {
                background-color: #e83f3f;
            }
            QScrollArea {
                background-color: #282c35;
                border: 1px solid #d0d0d0;
            }
            QLabel {
                color: white;
            }
        """)

    def create_input_fields_layout(self):
        layout = QFormLayout()

        for i in range(len(self.latitude_inputs)):
            layout.addRow(f'Waypoint {i + 1} - Latitude:', self.latitude_inputs[i])
            layout.addRow(f'Waypoint {i + 1} - Longitude:', self.longitude_inputs[i])
            layout.addRow(f'Waypoint {i + 1} - Altitude:', self.altitude_inputs[i])
            layout.addRow(f'Action at Waypoint {i + 1}:', self.action_comboboxes[i])
            layout.addRow(f'Duration at Waypoint {i + 1} (seconds):', self.duration_inputs[i])

        return layout

    def create_input_fields(self):
        try:
            num_waypoints = int(self.num_waypoints_input.text())

            for i in range(num_waypoints):
                latitude_input = QLineEdit(self)
                longitude_input = QLineEdit(self)
                altitude_input = QLineEdit(self)
                action_combobox = QComboBox(self)
                action_combobox.addItems(['Loiter', 'Land', 'RTL'])
                duration_input = QLineEdit(self)

                self.latitude_inputs.append(latitude_input)
                self.longitude_inputs.append(longitude_input)
                self.altitude_inputs.append(altitude_input)
                self.action_comboboxes.append(action_combobox)
                self.duration_inputs.append(duration_input)

            self.layout().addLayout(self.create_input_fields_layout())
        except ValueError:
            self.show_error_message('Invalid input. Please enter a valid number of waypoints.')

    def get_waypoints_actions_durations(self):
        waypoints_actions_durations = []
        for lat_input, lon_input, alt_input, action_combobox, duration_input in zip(
            self.latitude_inputs, self.longitude_inputs, self.altitude_inputs, self.action_comboboxes, self.duration_inputs
        ):
            lat = float(lat_input.text())
            lon = float(lon_input.text())
            alt = float(alt_input.text())
            action = action_combobox.currentText()
           
            try:
                duration = float(duration_input.text())
            except ValueError:
                self.show_error_message(f'Invalid duration at waypoint. Please enter a valid number for waypoint {len(waypoints_actions_durations) + 1}.')
                return None

            waypoints_actions_durations.append((lat, lon, alt, action, duration))
        return waypoints_actions_durations

    def start_drone_control(self):
        waypoints_actions_durations = self.get_waypoints_actions_durations()

        if waypoints_actions_durations is None:
            return

        try:
            connection_string = '/dev/ttyACM0'
            print('Connecting to vehicle on: %s' % connection_string)
            vehicle = self.connect_drone(connection_string)

            self.arm_and_takeoff(vehicle, 2)  

            print("Set default/target airspeed to 2")
            vehicle.airspeed = 2

            for i, (lat, lon, alt, action, duration) in enumerate(waypoints_actions_durations):
                point = LocationGlobalRelative(lat, lon, alt)
                print(f"Going to waypoint {i + 1}: {point} with action: {action}")

                vehicle.simple_goto(point, airspeed=2)

                while True:
                    current_location = vehicle.location.global_relative_frame
                    distance = geodesic((current_location.lat, current_location.lon), (lat, lon)).meters
                    print(" Distance to waypoint: {}".format(distance))
                    if distance < 1:
                        print("Reached waypoint")
                        break
                    time.sleep(1)

                self.perform_action(vehicle, action)

                self.wait_at_waypoint(duration)

            print("Returning to Launch")
            vehicle.mode = VehicleMode("RTL")
            print("Close vehicle object")
            vehicle.close()

        except Exception as e:
            self.show_error_message(f"Error during drone control: {e}")

        finally:
            for lat_input, lon_input, alt_input, action_combobox, duration_input in zip(
                self.latitude_inputs, self.longitude_inputs, self.altitude_inputs,
                self.action_comboboxes, self.duration_inputs
            ):
                lat_input.setDisabled(False)
                lon_input.setDisabled(False)
                alt_input.setDisabled(False)
                action_combobox.setDisabled(False)
                duration_input.setDisabled(False)
            self.num_waypoints_input.setDisabled(False)
            self.start_button.setDisabled(False)

    def perform_action(self, vehicle, action):
        if action == 'Loiter':
            print("Performing Loiter action")
            self.loiter_action(vehicle)
        elif action == 'Land':
            print("Performing Land action")
            self.land_action(vehicle)
        elif action == 'RTL':
            print("Performing RTL action")
            self.rtl_action(vehicle)

    def loiter_action(self, vehicle):
        vehicle.mode = VehicleMode("LOITER")

    def land_action(self, vehicle):
        vehicle.mode = VehicleMode("LAND")

    def rtl_action(self, vehicle):
        vehicle.mode = VehicleMode("RTL")

    def wait_at_waypoint(self, duration):
        print(f"Waiting at waypoint for {duration} seconds...")
        time.sleep(duration)

    def connect_drone(self, connection_string):
        print("Connecting to vehicle on: %s" % connection_string)
        vehicle = connect(connection_string, baud=57600, wait_ready=True)
        return vehicle

    def arm_and_takeoff(self, vehicle, aTargetAltitude):
        print("Arming motors")
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        while not vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)
        print("Taking off!")
        vehicle.simple_takeoff(aTargetAltitude)
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()

def run_app():
    app = QApplication(sys.argv)
    window = DroneControlUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()