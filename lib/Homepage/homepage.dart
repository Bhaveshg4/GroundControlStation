import 'package:flutter/material.dart';
import 'package:flutter_application_1/StartMission/MissionPlanner.dart';

class Homepage extends StatelessWidget {
  const Homepage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue.shade100,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 40),
                const Text(
                  "Welcome PilotX,",
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF0A4E85),
                  ),
                ),
                const Text(
                  "Select an action for UAV",
                  style: TextStyle(
                    fontSize: 22,
                    color: Color(0xFF0A4E85),
                  ),
                ),
                const SizedBox(height: 20),
                const Align(
                  alignment: Alignment.center,
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.0),
                    child: Text(
                      "“Drones overall will be more impactful than I think people recognize, in positive ways to help society.”",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontStyle: FontStyle.italic,
                        fontSize: 16,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 30),
                _buildActionCard(
                  title: "Start a Mission",
                  description:
                      "Initiate a new UAV mission with real-time tracking",
                  icon: Icons.flight_takeoff,
                  onPressed: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => DroneControlPage()));
                  },
                ),
                _buildActionCard(
                  title: "View Flight Parameteres",
                  description: "Check paramteres like altitude and speed",
                  icon: Icons.history,
                  onPressed: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => DroneControlPage()));
                  },
                ),
                _buildActionCard(
                  title: "Track Location",
                  description: "Track GPS location of UAV",
                  icon: Icons.location_on_outlined,
                  onPressed: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => DroneControlPage()));
                  },
                ),
                _buildActionCard(
                  title: "Emergency Protocols Guide",
                  description: "Activate emergency procedures and support",
                  icon: Icons.warning,
                  onPressed: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => DroneControlPage()));
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Helper Widget for Action Cards
  Widget _buildActionCard({
    required String title,
    required String description,
    required IconData icon,
    required VoidCallback onPressed,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [
            BoxShadow(
              color: Colors.black26,
              blurRadius: 8,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: ListTile(
          leading: CircleAvatar(
            backgroundColor: Colors.blue.shade300,
            child: Icon(icon, color: Colors.white, size: 28),
          ),
          title: Text(
            title,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0A4E85),
            ),
          ),
          subtitle: Text(
            description,
            style: TextStyle(
              color: Colors.grey.shade700,
            ),
          ),
          trailing: IconButton(
            icon: const Icon(Icons.arrow_forward_ios, color: Color(0xFF0A4E85)),
            onPressed: onPressed,
          ),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
      ),
    );
  }
}
