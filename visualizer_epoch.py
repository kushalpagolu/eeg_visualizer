from realtime_visualizer import RealtimeEEGVisualizer
#from realtime_visualizer_updated import RealtimeEEGVisualizer
from kalman_filter import KalmanFilter
from emotive_streamer import EmotivStreamer
import hid
from Crypto.Cipher import AES
import struct
from datetime import datetime
from matplotlib.animation import FuncAnimation
from collections import deque
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from threading import Thread


def save_data_continuously(data_store):
    while True:
        if data_store:
            filename = f"eeg_gyro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df = pd.DataFrame(data_store)
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            data_store.clear()

if __name__ == "__main__":
    emotiv = EmotivStreamer()
    visualizer = RealtimeEEGVisualizer()
    kalman_x, kalman_y = KalmanFilter(), KalmanFilter()

    def data_generator():
        while True:
            packet = emotiv.read_packet()
            if packet:
                filtered_gyro_x = kalman_x.update(packet['gyro_x'])
                filtered_gyro_y = kalman_y.update(packet['gyro_y'])
                visualizer.gyro_x_buffer.append(filtered_gyro_x)
                visualizer.gyro_y_buffer.append(filtered_gyro_y)
                print({filtered_gyro_x, filtered_gyro_y})

                eeg_channels = packet['eeg']
                for i, value in enumerate(eeg_channels):
                    visualizer.data_buffers[i].append(value)
                emotiv.data_store.append(packet)
                
            yield None

    if emotiv.connect():
        try:
            ani = FuncAnimation(
                visualizer.fig,
                visualizer.update,
                frames=data_generator,
                interval=500,  # Stream data every half a second
                cache_frame_data=False
            )
            #plt.show()
        except KeyboardInterrupt:
            print("Session terminated.")
            emotiv.device.close()

            # Save data when the session is finished
            save_data_continuously(emotiv.data_store)
