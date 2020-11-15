#!/usr/bin/env python
# -*- charset utf8 -*-

import pyaudio
import numpy
import math
import matplotlib.pyplot as plt
import matplotlib.animation
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
plt.xkcd()
numpy.seterr(divide = 'ignore')

RATE = 44100
BUFFER = 882*2


p = pyaudio.PyAudio()

stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFFER
)

fig = plt.figure()
line1 = plt.plot([],[])[0]
line2 = plt.plot([],[])[0]

r = numpy.arange(0,int(RATE/2+1),int(RATE/BUFFER))
l = len(r)

freqs = [0]

def the_same(lst, start, stop):
    for item in range(start, stop):
        if lst[item] != lst[item+1]:
            return (False, 0)
    return (lst[start], True)


def config_threshold():
    noise = []
    print("Configuring the noise...")
    for i in range(100):
        try:
            data = numpy.fft.rfft(numpy.fromstring(
                stream.read(BUFFER), dtype=numpy.float32)
            )

        except IOError:
            pass
        data = numpy.log10(numpy.sqrt(
                numpy.real(data)**2+numpy.imag(data)**2) / BUFFER) * 10
        mean = data.mean()

        if mean > -50:
            noise.append(mean)
            print(f"Actual noise mean: {mean}")
        else:
            print("ERROR :: -inf")
    noise = numpy.array(noise)
    print(f"MEAN: {noise.mean()}")
    return noise.mean() + 15

THRESHOLD = config_threshold()
print(THRESHOLD)



def init_line():
        line1.set_data(r, [-1000]*l)
        line2.set_data(r, [-1000]*l)
        return (line1,line2,)

def check_freq(data):
    if numpy.max(data) > THRESHOLD and r[numpy.argmax(data)] > 100:
        freqs.append(r[numpy.argmax(data)])
    if len(freqs) > 6:
        val, result = the_same(freqs, -6, -1)
        if result and val != freqs[0]:
            print(f"New Frequency: {val}Hz")
            freqs[0] = val

def check_clap(data):
    if data.mean() > THRESHOLD:
        print("Clap!")
        return True
    else:
        return False

def update_line(i):
    try:
        data = numpy.fft.rfft(numpy.fromstring(
            stream.read(BUFFER), dtype=numpy.float32)
        )
    except IOError:
        pass
    data = numpy.log10(numpy.sqrt(
            numpy.real(data)**2+numpy.imag(data)**2) / BUFFER) * 10
    check_freq(data)
    check_clap(data)
        #print(f"new frequency detected: {r[numpy.argmax(data)]}: {numpy.max(data)}dB")
    line1.set_data(r, data)
    line2.set_data(numpy.maximum(line1.get_data(), line2.get_data()))
    plt.axhline(y=THRESHOLD)

    return (line1,line2,)
plt.xlim(0, RATE/2+1)
plt.ylim(-60, 0)
plt.xlabel('Frequency')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()
plt.xlim(0, 3000)

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()
