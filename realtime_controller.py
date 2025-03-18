import hid
from Crypto.Cipher import AES
import struct
from datetime import datetime
import socket
import threading
import time

# ===================== Emotiv Headset Streamer =====================
class EmotivStreamer:
    """
    Reads EEG and Gyro data from Emotiv Epoch X.
    """
    def __init__(self):
        self.vid = 0x1234
        self.pid = 0xed02
        self.device = None
        self.cipher = None
        self.cypher_key = bytes.fromhex("31003554381037423100354838003750")
    
    def connect(self):
        """
        Establishes connection with the Emotiv Epoch X headset.
        """
        try:
            self.device = hid.device()
            self.device.open(self.vid, self.pid)
            self.device.set_nonblocking(1)
            self.cipher = AES.new(self.cypher_key, AES.MODE_ECB)
            print(f"Connected to Emotiv device {self.vid:04x}:{self.pid:04x}")
            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False

    def read_packet(self):
        """
        Reads and decrypts EEG and Gyro data from the headset.
        """
        encrypted = bytes(self.device.read(32))
        if not encrypted:
            return None
        decrypted = self.cipher.decrypt(encrypted)
        return {
            'timestamp': datetime.now().isoformat(),
            'gyro_x': decrypted[29] - 102,  # Normalize X-axis gyro data
            'gyro_y': decrypted[30] - 204,  # Normalize Y-axis gyro data
            'eeg': [int.from_bytes(decrypted[i:i+2], 'big', signed=True) for i in range(1, 29, 2)]
        }

# ===================== DJI Tello Drone Controller =====================
class DroneController:
    """
    Sends commands to the DJI Tello drone over UDP.
    """
    def __init__(self):
        self.tello_address = ('192.168.10.1', 8889)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 9000))
        self.running = True
        self.response_thread = threading.Thread(target=self.receive_response)
        self.response_thread.start()

    def send_command(self, command):
        """
        Sends a command to the Tello drone.
        """
        try:
            print(f"Sending command: {command}")
            self.sock.sendto(command.encode('utf-8'), self.tello_address)
        except Exception as e:
            print(f"Error sending command: {str(e)}")

    def receive_response(self):
        """
        Listens for responses from the drone.
        """
        while self.running:
            try:
                response, _ = self.sock.recvfrom(1024)
                print(f"Drone response: {response.decode('utf-8')}")
            except Exception:
                pass

    def takeoff(self):
        self.send_command("command")
        time.sleep(1)
        self.send_command("takeoff")

    def land(self):
        self.send_command("land")

    def move_forward(self, distance=50):
        self.send_command(f"forward {distance}")

    def move_backward(self, distance=50):
        self.send_command(f"back {distance}")

    def turn_left(self, degrees=30):
        self.send_command(f"ccw {degrees}")

    def turn_right(self, degrees=30):
        self.send_command(f"cw {degrees}")

# ===================== Head Movement Classifier =====================
class HeadMovementClassifier:
    """
    Classifies head movements based on gyro data and maps them to drone commands.
    """
    def __init__(self, threshold=15):
        self.threshold = threshold  # Sensitivity for detecting movement

    def classify_movement(self, gyro_x, gyro_y):
        """
        Determines movement based on gyro data.
        """
        if gyro_y > self.threshold:
            return "forward"
        elif gyro_y < -self.threshold:
            return "backward"
        elif gyro_x > self.threshold:
            return "right"
        elif gyro_x < -self.threshold:
            return "left"
        return None  # No movement detected

# ===================== Real-Time Controller =====================
class RealTimeController:
    """
    Integrates EEG/Gyro data with the drone control system in real time.
    """
    def __init__(self):
        self.emotiv = EmotivStreamer()
        self.drone = DroneController()
        self.classifier = HeadMovementClassifier()
        self.running = True

    def start(self):
        """
        Starts real-time control, continuously reading gyro data and sending drone commands.
        """
        if not self.emotiv.connect():
            print("Failed to connect to Emotiv. Exiting...")
            return

        self.drone.takeoff()
        print("Real-time control started. Move head to control the drone.")

        try:
            while self.running:
                data = self.emotiv.read_packet()
                if data:
                    movement = self.classifier.classify_movement(data['gyro_x'], data['gyro_y'])
                    if movement:
                        self.execute_command(movement)
                time.sleep(0.1)  # Adjust for responsiveness
        except KeyboardInterrupt:
            print("Stopping real-time control.")
        finally:
            self.drone.land()
            self.drone.running = False

    def execute_command(self, command):
        """
        Executes a movement command on the drone.
        """
        if command == "forward":
            self.drone.move_forward()
        elif command == "backward":
            self.drone.move_backward()
        elif command == "left":
            self.drone.turn_left()
        elif command == "right":
            self.drone.turn_right()

# ===================== Run the System =====================
if __name__ == "__main__":
    controller = RealTimeController()
    controller.start()
