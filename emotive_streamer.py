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

class EmotivStreamer:
    def __init__(self):
        self.vid = 0x1234
        self.pid = 0xed02
        self.device = None
        self.cipher = None
        self.cypher_key = bytes.fromhex("31003554381037423100354838003750")
        self.filename = f"eeg_gyro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.data_store = []

    def connect(self):
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
        encrypted = bytes(self.device.read(32))
        if not encrypted:
            return None
        decrypted = self.cipher.decrypt(encrypted)
        return {
            'timestamp': datetime.now().isoformat(),
            'counter': decrypted[0],
            'gyro_x': decrypted[29] - 102,
            'gyro_y': decrypted[30] - 204,
            'eeg': [int.from_bytes(decrypted[i:i+2], 'big', signed=True) for i in range(1, 29, 2)],
            'battery': (decrypted[31] & 0x01) * 100
        }
