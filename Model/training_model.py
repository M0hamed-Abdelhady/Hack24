import sys
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.src.layers import Reshape
from keras.src.utils import to_categorical


def normalize(spectrogram, max=10000) -> np.array:
    spectrogram = np.clip(spectrogram, 0, max)
    spectrogram = spectrogram / max
    return spectrogram


real_data = np.load('dataset/real.npz')
fake_data = np.load('dataset/fake.npz')
real_labels = np.array([1] * 750)
fake_labels = np.array([0] * 750)

x_real = np.array([normalize(s) for s in real_data['x']])
x_fake = np.array([normalize(s) for s in fake_data['x']])

x_train = np.concatenate((x_real[:600], x_fake[:600]))
x_test = np.concatenate((x_real[600:], x_fake[600:]))
y_train = np.concatenate((real_labels[:600], fake_labels[:600]))
y_test = np.concatenate((real_labels[600:], fake_labels[600:]))

y_train = to_categorical(y_train, num_classes=3)
y_test = to_categorical(y_test, num_classes=3)

# Build the model
model = Sequential()

model.add(Reshape((1998, 101, 1), input_shape=(1998, 101)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(3, activation='softmax'))

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.fit(x_train, y_train, epochs=10, batch_size=32)

test_loss, test_acc = model.evaluate(x_test, y_test)

model.save('spectrogram.h5')
