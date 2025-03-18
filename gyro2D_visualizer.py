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
        self.fig, axes = plt.subplots(2, 1, figsize=(16, 10))  # EEG + Gyro trajectory plot

        self.ax_eeg = axes[0]  # EEG Signal Plot
        self.ax_gyro = axes[1]  # Gyro 2D Motion Plot

        # EEG Signal Plot (Multiple Channels)
        colors = plt.cm.viridis(np.linspace(0, 1, num_channels))
        self.lines = [self.ax_eeg.plot([], [], label=self.channel_names[i], color=colors[i])[0] 
                      for i in range(self.num_channels)]
        self.ax_eeg.set_title("Real-time EEG Signals (14 Channels)")
        self.ax_eeg.set_xlabel("Sample Index")
        self.ax_eeg.set_ylabel("EEG Signal (µV)")
        self.ax_eeg.legend(loc="upper right", fontsize=8)
        self.ax_eeg.grid(True, alpha=0.4)

        # Gyro 2D Trajectory Plot (Head Movement)
        self.line_gyro_traj, = self.ax_gyro.plot([], [], color='cyan', alpha=0.8, label="Head Movement Path")
        self.point_gyro, = self.ax_gyro.plot([], [], 'ro', markersize=8, label="Current Position")  # Latest point

        self.ax_gyro.set_title("Real-time Head Movement (Gyro X vs Gyro Y)")
        self.ax_gyro.set_xlabel("Gyro X (Left-Right)")
        self.ax_gyro.set_ylabel("Gyro Y (Up-Down)")
        self.ax_gyro.set_xlim(-100, 100)
        self.ax_gyro.set_ylim(-100, 100)
        self.ax_gyro.legend()
        self.ax_gyro.grid(True, alpha=0.4)

    def update(self, frame):
    # Update EEG data
        for i, line in enumerate(self.lines):
            if len(self.data_buffers[i]) > 0:
                line.set_data(range(-len(self.data_buffers[i]), 0), self.data_buffers[i])

        self.ax_eeg.relim()
        self.ax_eeg.autoscale_view()

        # Update Gyro 2D Trajectory Plot
        if len(self.gyro_x_buffer) > 1:
            self.line_gyro_traj.set_data(self.gyro_x_buffer, self.gyro_y_buffer)
            self.point_gyro.set_data([self.gyro_x_buffer[-1]], [self.gyro_y_buffer[-1]])  # ✅ Fix: Wrap in lists

        return self.lines + [self.line_gyro_traj, self.point_gyro]
