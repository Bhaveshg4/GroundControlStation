import 'package:flutter/material.dart';
import 'package:firebase_database/firebase_database.dart';

class DroneControlPage extends StatefulWidget {
  @override
  _DroneControlPageState createState() => _DroneControlPageState();
}

class _DroneControlPageState extends State<DroneControlPage> {
  final DatabaseReference _droneRef =
      FirebaseDatabase.instance.ref().child('drone');

  String _gpsLocation = "Latitude: 0, Longitude: 0";
  double _speed = 0.0;
  final TextEditingController _altitudeController = TextEditingController();
  final List<Map<String, dynamic>> _waypoints = [];
  final TextEditingController _waypointLatController = TextEditingController();
  final TextEditingController _waypointLonController = TextEditingController();
  final TextEditingController _waypointAltController = TextEditingController();

  void _armDrone() {
    _droneRef.child('_arm').set('1111');
  }

  void _disarmDrone() {
    _droneRef.child('_disarm').set('0000');
  }

  void _landDrone() {
    _droneRef.child('_landed').set('1010');
  }

  void _takeoffDrone() {
    if (_altitudeController.text.isNotEmpty) {
      String command =
          '0101${_altitudeController.text}'; // Example command format
      _droneRef.child('_takeoff').set(command);
    }
  }

  void _navigateToWaypoints() {
    _droneRef.child('_automatedpath').set('1100');
    for (var waypoint in _waypoints) {
      _droneRef.child('waypoints').push().set(waypoint);
    }
  }

  void _listenToDroneData() {
    _droneRef.child('gpsLocation').onValue.listen((event) {
      final data = event.snapshot.value
          as Map<dynamic, dynamic>?; // Cast to the correct type
      if (data != null) {
        setState(() {
          _gpsLocation =
              "Latitude: ${data['latitude']}, Longitude: ${data['longitude']}";
        });
      }
    });

    _droneRef.child('speed').onValue.listen((event) {
      final data = event.snapshot.value
          as Map<dynamic, dynamic>?; // Cast to the correct type
      if (data != null) {
        setState(() {
          _speed = (data['value'] as num).toDouble();
        });
      }
    });
  }

  void _addWaypoint() {
    if (_waypointLatController.text.isNotEmpty &&
        _waypointLonController.text.isNotEmpty &&
        _waypointAltController.text.isNotEmpty) {
      final waypoint = {
        'latitude': double.tryParse(_waypointLatController.text),
        'longitude': double.tryParse(_waypointLonController.text),
        'altitude': double.tryParse(_waypointAltController.text),
      };

      setState(() {
        _waypoints.add(waypoint);
        _waypointLatController.clear();
        _waypointLonController.clear();
        _waypointAltController.clear();
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _listenToDroneData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Drone Control'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('GPS Location: $_gpsLocation',
                style: const TextStyle(fontSize: 16)),
            Text('Drone Speed: ${_speed.toStringAsFixed(2)} m/s',
                style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            TextField(
              controller: _altitudeController,
              decoration:
                  const InputDecoration(labelText: 'Altitude for Takeoff (m)'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(onPressed: _armDrone, child: const Text('Arm')),
                ElevatedButton(
                    onPressed: _disarmDrone, child: const Text('Disarm')),
              ],
            ),
            const SizedBox(height: 10),
            ElevatedButton(
                onPressed: _takeoffDrone, child: const Text('Takeoff')),
            ElevatedButton(onPressed: _landDrone, child: const Text('Land')),
            const SizedBox(height: 20),
            const Text('Add Waypoint:', style: TextStyle(fontSize: 18)),
            TextField(
              controller: _waypointLatController,
              decoration: const InputDecoration(labelText: 'Waypoint Latitude'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _waypointLonController,
              decoration:
                  const InputDecoration(labelText: 'Waypoint Longitude'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _waypointAltController,
              decoration:
                  const InputDecoration(labelText: 'Waypoint Altitude (m)'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _addWaypoint,
              child: const Text('Add Waypoint'),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: _waypoints.length,
                itemBuilder: (context, index) {
                  final waypoint = _waypoints[index];
                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    child: ListTile(
                      title: Text('Waypoint ${index + 1}'),
                      subtitle: Text(
                          'Lat: ${waypoint['latitude']}, Lon: ${waypoint['longitude']}, Alt: ${waypoint['altitude']} m'),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () {
                          setState(() {
                            _waypoints.removeAt(index);
                          });
                        },
                      ),
                    ),
                  );
                },
              ),
            ),
            ElevatedButton(
              onPressed: _navigateToWaypoints,
              child: const Text('Navigate to Waypoints'),
            ),
          ],
        ),
      ),
    );
  }
}
