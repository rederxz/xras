import tensorflow as tf

def padding(padding):
    def pad_image(x):
        paddings = [[0, 0], [padding, padding], [padding, padding], [0, 0]]
        paddings = tf.constant(paddings)
        x = tf.pad(x, paddings, 'REFLECT')
        return x

    return keras.layers.Lambda(lambda x: pad_image(x))