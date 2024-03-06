import numpy as np
import tensorflow as tf


def normalize(spectrogram, max=10000) -> np.array:
    spectrogram = np.clip(spectrogram, 0, max)
    spectrogram = spectrogram / max
    return spectrogram


def adjust(spectrogram, x=1998, y=101) -> np.array:
    current_x, current_y = spectrogram.shape
    if current_x < x:
        top = (x - current_x) // 2
        bottom = x - current_x - top
        spectrogram = np.pad(spectrogram, ((top, bottom), (0, 0)), mode='edge')
    elif current_x > x:
        top = (current_x - x) // 2
        bottom = current_x - x - top
        spectrogram = spectrogram[top:current_x - bottom, :]
    if current_y < y:
        left = (y - current_y) // 2
        right = y - current_y - left
        spectrogram = np.pad(spectrogram, ((0, 0), (left, right)), mode='edge')
    elif current_y > y:
        left = (current_y - y) // 2
        right = current_y - y - left
        spectrogram = spectrogram[:, left:current_y - right]

    return spectrogram


def make_prediction(spectrogram):
    spectrogram = adjust(spectrogram)
    spectrogram = normalize(spectrogram)
    spectrogram = tf.reshape(spectrogram, (1, 1998, 101))
    model = tf.keras.models.load_model(R"D:\Projects\HackTrick24\Model\spectrogram_2.h5")
    prediction = model.predict(spectrogram)

    tmp = np.argmax(prediction[0])
    if tmp == 1:
        return 1
    return 0
