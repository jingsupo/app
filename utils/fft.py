import wave
import numpy as np
import matplotlib.pyplot as plt


path = r'D:\Desktop\data\iPhone按键音素材\dtmf-0.wav'


def wave_analysis(fp):
    f = wave.open(fp, 'rb')

    num = path[-5]
    params = f.getparams()

    nchannels, sampwidth, framerate, nframes = params[:4]
    print(nchannels, sampwidth, framerate, nframes)

    str_data = f.readframes(nframes)

    f.close()

    wave_data = np.frombuffer(str_data, dtype=np.short)

    wave_data.shape = -1, 1
    print(wave_data.shape)

    if nchannels == 2:
        wave_data.shape = -1, 2
    else:
        pass

    wave_data = wave_data.T

    time = np.arange(nframes) * (1.0 / framerate)

    plt.subplot(211)
    plt.plot(time, wave_data[0], 'r-')
    plt.xlabel('Time/s')
    plt.ylabel('Amplitude')
    plt.title('Num ' + num + ' time/amplitude')

    df = framerate / (nframes - 1)
    freq = [df * n for n in range(nframes)]
    transformed = np.fft.fft(wave_data[0])
    d = len(transformed) // 2
    while freq[d] > 4000:
        d -= 10
    freq = freq[:d]
    transformed = transformed[:d]
    for i, data in enumerate(transformed):
        transformed[i] = abs(data)

    plt.subplot(212)
    plt.plot(freq, transformed, 'b-')
    plt.xlabel('Freq/Hz')
    plt.ylabel('Amplitude')
    plt.title('Num ' + num + ' freq/amplitude')
    plt.show()

    local_max = []
    for i in np.arange(1, len(transformed) - 1):
        if transformed[i] > transformed[i-1] and transformed[i] > transformed[i+1]:
            local_max.append(transformed[i])
    local_max = sorted(local_max)
    loc = np.where(transformed == local_max[-1])
    max_freq = freq[loc[0][0]]
    loc = np.where(transformed == local_max[-2])
    min_freq = freq[loc[0][0]]
    print(max_freq, min_freq)
    return max_freq, min_freq


def main():
    x = []
    y = []
    for i in range(10):
        fp = r'D:\Desktop\data\iPhone按键音素材\dtmf-' + str(i) + '.wav'
        max_freq, min_freq = wave_analysis(fp)
        x.append(i)
        y.append(max_freq)
        x.append(i)
        y.append(min_freq)
    plt.scatter(x, y, marker='*')
    plt.show()


# main()


# wave_analysis(path)









