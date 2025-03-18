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

class RealtimeEEGVisualizer:
    def __init__(self, buffer_size=1000, num_channels=14):
        self.buffer_size = buffer_size
        self.num_channels = num_channels
        self.data_buffers = [deque(maxlen=buffer_size) for _ in range(num_channels)]
        self.gyro_x_buffer = deque(maxlen=buffer_size)
        self.gyro_y_buffer = deque(maxlen=buffer_size)

        # EEG channel names for Emotiv EPOC+
        self.channel_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2',
                              'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

        plt.style.use('dark_background')
        self.fig, axes = plt.subplots(15, 1, figsize=(16, 12), sharex=True)  # 14 EEG + 1 Gyro subplot
        #self.fig, axes = plt.subplots(2, 1, figsize=(16, 6), sharex=True)  # 1 EEG + 1 Gyro subplot

        self.ax_eeg = axes[:self.num_channels]  # First 14 rows for EEG channels
        self.ax_gyro = axes[self.num_channels:]  # Last row for gyro data

        # EEG Signal Plot
        colors = plt.cm.viridis(np.linspace(0, 1, num_channels))
        self.lines = [self.ax_eeg[i].plot([], [], label=self.channel_names[i], color=colors[i])[0] 
                    for i in range(self.num_channels)]
        for i, ax in enumerate(self.ax_eeg):
            #ax.set_title(self.channel_names[i])
            ax.set_xlabel("Sample Index")
            ax.set_ylabel("EEG Signal (µV)")
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.4)

        # Gyroscope Data Plot
        self.line_gyro_x, = self.ax_gyro[0].plot([], [], label="Gyro X", color='r')
        self.line_gyro_y, = self.ax_gyro[0].plot([], [], label="Gyro Y", color='b')
        self.ax_gyro[0].set_title("Real-time Gyro Data")
        self.ax_gyro[0].set_xlabel("Sample Index")
        self.ax_gyro[0].set_ylabel("Gyro Values")

        # self.ax_gyro.set_title("Real-time Gyro Data")
        # self.ax_gyro.set_xlabel("Sample Index")
        # self.ax_gyro.set_ylabel("Gyro Values")

        self.ax_gyro[0].legend()
        self.ax_gyro[0].grid(True, alpha=0.3)

    def update(self, frame):
        # Update EEG data
        for i, line in enumerate(self.lines):
            if len(self.data_buffers[i]) > 0:
                line.set_data(range(len(self.data_buffers[i])), self.data_buffers[i])
                self.ax_eeg[i].relim()
                self.ax_eeg[i].autoscale_view()

        # Update Gyro data
        if len(self.gyro_x_buffer) > 0:
            self.line_gyro_x.set_data(range(len(self.gyro_x_buffer)), self.gyro_x_buffer)
            self.line_gyro_y.set_data(range(len(self.gyro_y_buffer)), self.gyro_y_buffer)
            self.ax_gyro[0].relim()
            self.ax_gyro[0].autoscale_view()

        return self.lines + [self.line_gyro_x, self.line_gyro_y]