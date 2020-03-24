import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import struct
import time

# %matplotlib auto

CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

fig, (ax, ax2) = plt.subplots(2, figsize=(15, 8))

x = np.arange(0, 2 * CHUNK, 2)
x_fft = np.linspace(0, RATE, CHUNK)

line, = ax.plot(x, np.random.rand(CHUNK))
line_fft, = ax2.plot(x_fft, np.random.rand(CHUNK), '-', lw=1)

ax.set_xlim(0, 2 * CHUNK)
ax.set_ylim(0, 255)

ax2.set_xlim(20, RATE / 2)

print('stream started...')

frame_count = 0
start_time = time.time()

while True:
    data = stream.read(CHUNK)
    data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
    
    data_arr = np.array(data_int, dtype='b')[::2] + 128
    line.set_ydata(data_arr)
    
    y_fft = np.fft.fft(data_int)
    line_fft.set_ydata(np.abs(y_fft[0:CHUNK]) * 2 / (256 * CHUNK))
    
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1
    except:
        frame_rate = frame_count / (time.time() - start_time)
        print('stream stopped...')
        print('average frame rate = {:.0f} FPS'.format(frame_rate))
        break
