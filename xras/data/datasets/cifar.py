import tensorflow as tf
from tensorflow import keras

def cifar10(wrapped=True):
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
    x_train.astype('float32')
    x_test.astype('float32')
    x_train = x_train / 255.
    x_test = x_test / 255.

    x_train = (x_train - [0.4914, 0.4822, 0.4465]) / [0.247, 0.243, 0.261]
    x_test = (x_test - [0.4914, 0.4822, 0.4465]) / [0.247, 0.243, 0.261]
    y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)

    if wrapped:
        ds_train = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        ds_test = tf.data.Dataset.from_tensor_slices((x_test, y_test))
        return ds_train, ds_test
    else:
        return x_train, y_train, x_test, y_test
