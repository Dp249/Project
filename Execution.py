import numpy as np
import time
from face_detection import FaceDetection
from scipy import signal

# from sklearn.decomposition import FastICA


class Process:
    def __init__(self):
        self.frame_in = np.zeros((10, 10, 3), np.uint8)
        self.frame_out = np.zeros((10, 10, 3), np.uint8)
        self.frame_ROI = np.zeros((10, 10, 3), np.uint8)

        self.samples = []
        self.buffer_size = 400
        self.times = []
        self.data_buffer = []
        self.fps = 0
        self.fft = []
        self.freqs = []
        self.initial_time = time.time()
        self.face_detect = FaceDetection()
        self.bpm = 0
        self.bpms = []

    def reset(self):
        self.frame_in = np.zeros((10, 10, 3), np.uint8)
        self.frame_out = np.zeros((10, 10, 3), np.uint8)
        self.frame_ROI = np.zeros((10, 10, 3), np.uint8)
        self.samples = []
        self.times = []
        self.data_buffer = []
        self.fps = 0
        self.fft = []
        self.freqs = []
        self.initial_time = time.time()
        self.bpm = 0
        self.bpms = []

    def butter_bandpass(self, low_cut, high_cut, fs, order=5):
        nyquist_freq = 0.5 * fs

        # Normalize the frequency
        low = low_cut / nyquist_freq
        high = high_cut / nyquist_freq

        # if the high frequency is greater than 1, set it to 0.99
        if high > 1:
            high = 0.99

        b, a = signal.butter(order, [low, high], btype="band")

        # return the filter coefficients
        return b, a

    def butter_bandpass_filter(self, data, low_cut, high_cut, fs, order=5):
        # get the filter coefficients
        b, a = self.butter_bandpass(low_cut, high_cut, fs, order=order)

        # apply the filter
        return signal.lfilter(b, a, data)

    def extract_color(self, frame):
        green = np.mean(frame[:, :, 1])
        return green

    def run(self):
        frame, face, ROI1, ROI2, _ = self.face_detect.detect_face(self.frame_in)

        self.frame_out = frame
        self.frame_ROI = face

        # calculate average green value of 2 ROIs
        green1 = self.extract_color(ROI1)
        green2 = self.extract_color(ROI2)
        avg = (green1 + green2) / 2

        LENGTH = len(self.data_buffer)

        # remove outliers by comparing with the average of the buffer and the last value
        if abs(avg - np.mean(self.data_buffer)) > 10 and LENGTH > 99:
            avg = self.data_buffer[-1]

        self.times.append(time.time() - self.initial_time)
        self.data_buffer.append(avg)

        # only process in a fixed-size buffer
        if LENGTH > self.buffer_size:
            self.data_buffer = self.data_buffer[-self.buffer_size :]
            self.times = self.times[-self.buffer_size :]
            self.bpms = self.bpms[-self.buffer_size // 2 :]
            LENGTH = self.buffer_size

        # convert the buffer to numpy array
        processed = np.array(self.data_buffer)

        # if the buffer is full, start processing
        if LENGTH == self.buffer_size:
            # calculate the fps
            self.fps = float(LENGTH) / (self.times[-1] - self.times[0])

            # detrend the signal to avoid interference of light change
            processed = signal.detrend(processed)

            # interpolate the signal to make it evenly spaced
            even_times = np.linspace(self.times[0], self.times[-1], LENGTH)
            interpolated = np.interp(even_times, self.times, processed)

            # make the signal become more periodic (advoid spectral leakage)
            interpolated = np.hamming(LENGTH) * interpolated

            # normalization
            norm = interpolated / np.linalg.norm(interpolated)

            # calculate real FFT
            raw = np.fft.rfft(norm * 30)

            # get amplitude spectrum
            self.fft = np.abs(raw) ** 2

            # get the frequency
            self.freqs = float(self.fps) / LENGTH * np.arange(LENGTH / 2 + 1)
            freqs = 60.0 * self.freqs

            # the range of frequency that HR is supposed to be within
            idx = np.where((freqs > 50) & (freqs < 180))

            self.freqs = freqs[idx]
            self.fft = self.fft[idx]

            # find the peak of the spectrum
            peak = np.argmax(self.fft)

            # get the corresponding frequency
            self.bpm = self.freqs[peak]
            self.bpms.append(self.bpm)

            # passband 0.8-3Hz
            processed = self.butter_bandpass_filter(
                processed, 0.8, 3, self.fps, order=3
            )

        # update the samples
        self.samples = processed
