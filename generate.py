import numpy as np
import wave
import struct
import matplotlib.pyplot as plt

frequency = 440 # when 500Hz sth strange happens
num_samples = 48000

sampling_rate = 48000.0
amplitude = 16000
file = "test.wav"
sine_wave = [np.sin(2 * np.pi * frequency * x/sampling_rate) for x in range(num_samples)]


nframes=num_samples

comptype="NONE"

compname="not compressed"

nchannels=1

sampwidth=2

wav_file = wave.open(file, "w")
wav_file.setparams((nchannels, sampwidth, int(sampling_rate), nframes, comptype, compname))

for s in sine_wave:
   wav_file.writeframes(struct.pack('h', int(s*amplitude)))


frame_rate = 48000.0

infile = "output.wav"

num_samples = 48000

wav_file = wave.open(infile, 'r')

data = wav_file.readframes(num_samples)

wav_file.close()

data = struct.unpack('{n}h'.format(n=num_samples), data)


data = np.array(data)
data_fft = np.fft.fft(data)
frequencies = np.abs(data_fft)


print(f"The frequency is {np.argmax(frequencies)} Hz")
