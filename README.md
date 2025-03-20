# eeg_visualizer
Emotiv Epoch X eeg raw data streamer and data collector.


Overview of the Project

The main goal of the project is to control a DJI Tello drone in real-time using EEG (brain waves) and gyro data from an Emotiv Epoch X headset. The system classifies head movements (using gyro data) and translates them into drone commands (e.g., move forward, move backward, turn left, turn right). The EEG data is visualized in real-time, and both EEG and gyro data are saved continuously for further analysis.


Testing emotiv epoch x headset open source python code for classification and drone control. 

How the System Works

1. Connect to Emotiv Epoch X headset. The dongle needs to be connected to the usb of your windows or MAC.

The code reads gyro X/Y data for head movement classification and the EEG data is read for the visualizer, but currently only gyro is used for control.


Key Observations About Data

EEG Channel Extraction

Extracts 14 EEG channels (range(1, 29, 2)), which matches the EPOC/X's 14-electrode configuration. 

Each EEG value is parsed as a signed 16-bit integer from 2-byte segments.

Gyroscope Data
The adjustments decrypted - 102 and decrypted - 204 align with known calibration offsets for the EPOC/X's gyroscope. 

Valid gyro ranges are typically:

X-axis: 0–255 (centered at ~102)

Y-axis: 0–255 (centered at ~204)

Battery Level
The calculation (decrypted & 0x01) * 100 interprets the LSB of byte 31 as a boolean (0% or 100%).

What the Data Stream Contains

When connected via open-source Python code, the Emotiv EPOC/X streams:

Data Type	Description	Typical Values
counter	Packet sequence number	0–255 (8-bit)
gyro_x/gyro_y	Headset rotation (raw ADC)	0–255 (centered)
eeg	14-channel EEG (AF3–AF4) as μV	-8192–8191 (±327μV)
battery	0% or 100% (binary)	0 or 100


Connect to DJI Tello Drone.

Connect your tello drone by turning on the drone and connecting wifi to the Tello wifi.

How is it handled.

Code sends commands over UDP.
Starts with a takeoff command.
Can execute forward, backward, left, and right turns.

Classification of Head Movements

Tilt head forward → move forward
Tilt head backward → move backward
Turn head left → turn drone left
Turn head right → turn drone right
Real-time Loop

Continuously reads gyro data.

Detects movements and sends corresponding drone commands.

Stops upon keyboard interrupt (Ctrl+C) and lands the drone safely.


Key Components
EmotivStreamer - Reads data from the Emotiv Epoch X headset.
RealtimeEEGVisualizer - Visualizes EEG and gyro data in real-time.
Kalman Filter - Used for filtering the gyro data to smooth out the noise.
HeadMovementClassifier - Classifies head movements (forward, backward, left, right) based on gyro data.
DroneController - Sends commands to the DJI Tello drone using UDP.
Main Script (main.py) - Integrates all components and runs the system in real-time.

Step-by-Step Breakdown

Initialization and Connection

The EmotivStreamer class connects to the Emotiv Epoch X headset over HID (USB). It listens for packets of data containing EEG and gyro data (gyro_x and gyro_y).
The DroneController connects to the DJI Tello drone via UDP. It initializes communication and sends commands like "takeoff", "land", and movement commands (e.g., "forward", "backward").
The RealtimeEEGVisualizer initializes two subplots: one for the gyro data and another for the EEG data. The gyro data will be plotted in real-time, and the EEG data will also be visualized in real-time.
The Kalman filters (in kalman_filter.py) are applied to smooth the noisy gyro data coming from the Emotiv headset.
Data Collection (EEG and Gyro Data)

The data_generator function continuously reads data from the Emotiv headset. 

Each packet contains:
Gyro data (gyro_x, gyro_y): Used to track the head's movement.
EEG data: Captures brain wave activity.
The gyro data is filtered using Kalman filters to reduce noise, and the filtered data is added to buffers for real-time visualization.
The EEG data is directly added to buffers to be visualized.
Real-time Visualization

The RealtimeEEGVisualizer class handles the plotting of real-time data using Matplotlib.
The gyro data (both X and Y) is displayed in a real-time plot, showing the movement of the head.
The EEG data for each of the 14 channels is also plotted, showing brain wave activity in real-time.
This allows you to see both the brain activity and head movement data as it’s being captured from the headset.
Classifying Head Movements

The HeadMovementClassifier uses the gyro data (filtered gyro_x and gyro_y) to classify head movements:
Forward movement: If gyro_y (head tilt forward) exceeds a threshold.
Backward movement: If gyro_y (head tilt backward) is below a threshold.
Turn left: If gyro_x (head turn left) exceeds a threshold.
Turn right: If gyro_x (head turn right) exceeds a threshold.
When a movement is detected (e.g., head turns or tilts), the classifier returns a movement command, which is then sent to the drone.
Drone Control

Based on the classified head movement, the DroneController sends commands to the DJI Tello drone:
Forward: The drone moves forward by a predefined distance.
Backward: The drone moves backward.
Left: The drone turns left.
Right: The drone turns right.
The drone responds to these commands in real-time, executing the corresponding action.
Saving Data

The data_store contains all the captured data (EEG, gyro, timestamp). Every few seconds, this data is saved to an Excel file for future analysis.
This continuous saving ensures that data is logged even if the session is interrupted.
Real-Time Flow of the System
Here’s how everything works together in real time:

The EmotivStreamer connects to the Emotiv Epoch X headset and begins reading data packets. Each packet includes both EEG and gyro data.
The gyro data is passed through the Kalman filter to remove noise.
The filtered gyro data is then used by the HeadMovementClassifier to classify head movements (forward, backward, left, or right).
Depending on the classified movement, the DroneController sends the corresponding command to the DJI Tello drone.
Simultaneously, the RealtimeEEGVisualizer updates the plots for both EEG and gyro data in real-time, providing a visual representation of brain waves and head movements.
All the captured data is stored in a data buffer and saved periodically to an Excel file.
The process repeats in a loop, continuously reading new data from the Emotiv headset, classifying movements, controlling the drone, and updating the visualizations.
Interactive Session Example
Step 1: You connect the Emotiv Epoch X headset to your computer.
Step 2: The system begins collecting both EEG and gyro data from the headset.
Step 3: The gyro data is smoothed using the Kalman filter, and the system detects head movements such as tilting forward, turning left, etc.
Step 4: The drone executes the movement commands (e.g., move forward if you tilt your head forward).
Step 5: As this happens, you can see the real-time visualization of both EEG and gyro data on the screen.
Step 6: The data is saved continuously to an Excel file for further analysis.
Conclusion
The Emotiv Epoch X headset provides real-time EEG and gyro data, which is filtered and used for head movement classification.

The gyro data is classified using the ML model (HeadMovementClassifier).
Safety checks are performed before sending commands to the drone.
The drone controller moves the drone based on the classified movement (forward, backward, left, or right).
The visualizer updates in real time.


The classified head movements are translated into drone commands, allowing you to control the drone through your head movements.
Real-time visualization of both EEG and gyro data gives immediate feedback about the brain activity and head movement, while the Kalman filter ensures smooth and reliable gyro data.
Finally, all captured data is saved to a file for later analysis.
This project showcases how brain-computer interface (BCI) technologies and sensor fusion (EEG + gyro data) can be used for real-time control of drones and visualization of brain activity.

## Setup Instructions

### 1. Clone the repository
Clone the repository to your local machine.

```bash
git clone https://github.com/your-username/your-repo-name.git
cd emotiv_test

# Create a virtual environment
python -m venv env

# Activate the virtual environment
# For Windows:
env\Scripts\activate

# For macOS/Linux:
source env/bin/activate


# Install all the dependencies

pip install -r requirements.txt

This will install the necessary packages such as:

hid: For interacting with the Emotiv device.

#Macos
brew install hidapi

pycryptodome: For AES decryption of data from the Emotiv device.
matplotlib: For visualizing EEG and gyro data in real-time.
numpy: For numerical operations.
pandas: For saving data to an Excel file.
scikit-learn: For any machine learning algorithms (if using classical ML).
tensorflow: For neural network or deep learning model training.


Connect the Emotiv Epoch X Headset
Ensure the Emotiv Epoch X headset is properly connected to your computer.

5. Run the Code
Start the real-time visualization and data processing.

python visualizer.py

6. Testing Without Drone (Optional)
If you want to test the system without connecting the drone, ensure the drone controller is set to **False** in the code and run the script.

7. Testing With Drone
To connect the DJI Tello drone, ensure it is connected to the same network and run the script with the drone connected.


Considerations for Newcomers
Ensure that the Emotiv Epoch X headset is connected to the computer before running the script. The code uses the usb connecton to the headset to retrieve the encrypted data.

If working with the DJI Tello drone, the drone should be connected to the same network and properly configured for communication. You will be connected to the Tello wifi to control the drone. The code will be run locally for the visualizer and the drone control to work.


Summary
✅ EEG & Gyro Data Collection
✅ Real-time Visualization
✅ Head Movement Classification
✅ Drone Control with Brain Activity & Gyro
✅ Data Saving for Analysis
