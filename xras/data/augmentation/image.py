import tensorflow as tf
from tensorflow import keras

def padding(padding=4):
    def pad_image(x):
        paddings = [[0, 0], [padding, padding], [padding, padding], [0, 0]]
        paddings = tf.constant(paddings)
        x = tf.pad(x, paddings, 'REFLECT')
        return x
    return keras.layers.Lambda(lambda x: pad_image(x))

def mixup(batch_one, batch_two, alpha=1.0):

  def beta_dist(size):
    gamma_1_sample = tf.random.gamma(shape=[size], alpha=alpha)
    gamma_2_sample = tf.random.gamma(shape=[size], alpha=alpha)
    return gamma_1_sample / (gamma_1_sample + gamma_2_sample)
  
  image_one, label_one = batch_one
  image_two, label_two = batch_two

  batch_size = tf.shape(label_one)[0]
  gamma = beta_dist(batch_size)
  gamma_image = tf.reshape(gamma, (batch_size, 1, 1, 1))
  gamma_label = tf.reshape(gamma, (batch_size, 1))

  image = gamma_image * image_one + (tf.ones_like(gamma_image) - gamma_image) * image_two
  label = gamma_label * label_one + (tf.ones_like(gamma_label) - gamma_label) * label_two

  return (image, label)


def random_erasing(image, p=0.5, s_l=0.02, s_h=0.4, r_1=0.3, r_2=1/0.3):

  height = image.get_shape()[0]
  width = image.get_shape()[1]
  s = height * width

  if tf.random.uniform(()) < p:

    while(tf.constant(True, dtype=tf.bool)):
      # random area
      s_e = tf.random.uniform((), 0., s)
      # random aspect ratio
      r_e = tf.random.uniform((), r_1, r_2)
      # random height and width
      h_e = tf.cast(tf.math.round(tf.math.sqrt(s_e * r_e)), tf.int32)
      w_e = tf.cast(tf.math.round(tf.math.sqrt(s_e / r_e)), tf.int32)
      # random postion
      x_e = tf.cast(tf.math.round(tf.random.uniform((), 0., width)), tf.int32)
      y_e = tf.cast(tf.math.round(tf.random.uniform((), 0., height)), tf.int32)

      if (x_e + w_e <= width) and (y_e + h_e <= height):
        break
    shelter = tf.random.uniform((w_e, h_e, 1), 0, 255, tf.float32)
    shelter = tf.repeat(shelter, 3, axis=-1)
    high = image[: , 0:y_e, :]
    mid_left = image[0: x_e, y_e:y_e+h_e, :]
    # mid_mid = image[x_e: x_e+w_e, y_e:y_e+h_e, :]
    mid_right = image[x_e+w_e: width, y_e:y_e+h_e, :]
    low = image[:, y_e+h_e: height, :]

    mid = tf.concat([mid_left, shelter, mid_right], 0) # along x axis
    image = tf.concat([high, mid, low], 1) # along y axis
        
  return image

def random_erasing(image, p=0.5, s_l=0.02, s_h=0.4, r_1=0.3, r_2=1/0.3):

  height = image.get_shape()[0]
  width = image.get_shape()[1]
  s = height * width

  if tf.random.uniform(()) < p:

    x_e = tf.constant(0)
    y_e = tf.constant(0)
    h_e = tf.constant(0)
    w_e = tf.constant(0)

    while(tf.constant(True, dtype=tf.bool)):
      # random area
      s_e = tf.random.uniform((), 0., s)
      # random aspect ratio
      r_e = tf.random.uniform((), r_1, r_2)
      # random height and width
      h_e = tf.cast(tf.math.round(tf.math.sqrt(s_e * r_e)), tf.int32)
      w_e = tf.cast(tf.math.round(tf.math.sqrt(s_e / r_e)), tf.int32)
      # random postion
      x_e = tf.cast(tf.math.round(tf.random.uniform((), 0., width)), tf.int32)
      y_e = tf.cast(tf.math.round(tf.random.uniform((), 0., height)), tf.int32)

      if (x_e + w_e <= width) and (y_e + h_e <= height):
        break

    # shelter = tf.cast(tf.random.uniform((w_e, h_e, 3), 0, 256, tf.int32), tf.float32)

    shelter_1 = tf.random.normal((w_e, h_e, 1), mean=0.4914, stddev=0.2023, dtype=tf.float32)
    shelter_2 = tf.random.normal((w_e, h_e, 1), mean=0.4822, stddev=0.1994, dtype=tf.float32)
    shelter_3 = tf.random.normal((w_e, h_e, 1), mean=0.4465, stddev=0.2010, dtype=tf.float32)
    shelter = tf.concat([shelter_1, shelter_2, shelter_3], -1)

    # mean = [0.4914, 0.4822, 0.4465]
    # shelter_1 = tf.fill((w_e, h_e, 1), mean[0])
    # shelter_2 = tf.fill((w_e, h_e, 1), mean[1])
    # shelter_3 = tf.fill((w_e, h_e, 1), mean[2])
    # shelter = tf.concat([shelter_1, shelter_2, shelter_3], -1)

    high = image[: , 0:y_e, :]
    mid_left = image[0: x_e, y_e:y_e+h_e, :]
    # mid_mid = image[x_e: x_e+w_e, y_e:y_e+h_e, :]
    mid_right = image[x_e+w_e: width, y_e:y_e+h_e, :]
    low = image[:, y_e+h_e: height, :]

    mid = tf.concat([mid_left, shelter, mid_right], 0) # along x axis
    image = tf.concat([high, mid, low], 1) # along y axis
        
  return image

def random_erasing_batch(image_batch, p=0.5, s_l=0.02, s_h=0.4, r_1=0.3, r_2=1/0.3):

  # some params to use later
  batch_size = image_batch.get_shape()[0]
  height = image_batch.get_shape()[1]
  width = image_batch.get_shape()[2]
  s = height * width

  # to cnt how many images
  cnt = tf.ones_like(image_batch[:, 0, 0, 0])
  cnt = tf.reduce_sum(cnt)
  i = tf.constant(0, tf.int32)

  # the host for new image batch
  new_image_batch = tf.ones_like(image_batch)

  while(tf.constant(True, tf.bool)):
    image = image_batch[i, :, :, :]

    # to RE image
    if tf.random.uniform(()) < p:

      x_e = tf.constant(0)
      y_e = tf.constant(0)
      h_e = tf.constant(0)
      w_e = tf.constant(0)

      while(tf.constant(True, dtype=tf.bool)):
        # random area
        s_e = tf.random.uniform((), 0., s)
        # random aspect ratio
        r_e = tf.random.uniform((), r_1, r_2)
        # random height and width
        h_e = tf.cast(tf.math.round(tf.math.sqrt(s_e * r_e)), tf.int32)
        w_e = tf.cast(tf.math.round(tf.math.sqrt(s_e / r_e)), tf.int32)
        # random postion
        x_e = tf.cast(tf.math.round(tf.random.uniform((), 0., width)), tf.int32)
        y_e = tf.cast(tf.math.round(tf.random.uniform((), 0., height)), tf.int32)

        if (x_e + w_e <= width) and (y_e + h_e <= height):
          break

      # shelter = tf.cast(tf.random.uniform((w_e, h_e, 3), 0, 256, tf.int32), tf.float32)

      shelter_1 = tf.random.normal((w_e, h_e, 1), mean=0.4914, stddev=0.2023, dtype=tf.float32)
      shelter_2 = tf.random.normal((w_e, h_e, 1), mean=0.4822, stddev=0.1994, dtype=tf.float32)
      shelter_3 = tf.random.normal((w_e, h_e, 1), mean=0.4465, stddev=0.2010, dtype=tf.float32)
      shelter = tf.concat([shelter_1, shelter_2, shelter_3], -1)

      # mean = [0.4914, 0.4822, 0.4465]
      # shelter_1 = tf.fill((w_e, h_e, 1), mean[0])
      # shelter_2 = tf.fill((w_e, h_e, 1), mean[1])
      # shelter_3 = tf.fill((w_e, h_e, 1), mean[2])
      # shelter = tf.concat([shelter_1, shelter_2, shelter_3], -1)

      # generate a new image by concatenating 5 parts
      high = image[: , 0:y_e, :]
      mid_left = image[0: x_e, y_e:y_e+h_e, :]
      mid_right = image[x_e+w_e: width, y_e:y_e+h_e, :]
      low = image[:, y_e+h_e: height, :]

      mid = tf.concat([mid_left, shelter, mid_right], 0) # along x axis
      image = tf.concat([high, mid, low], 1) # along y axis

    # install the new image to the host
    image = tf.expand_dims(image, 0)
    new_image_batch = tf.concat([new_image_batch[0:i], image, new_image_batch[i:-1]], 0)


    i = i + 1
    cnt = cnt - 1
    if (tf.cast(cnt, tf.int32) == tf.constant(0)):
      break
        
  return new_image_batch