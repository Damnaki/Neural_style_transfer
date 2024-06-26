# -*- coding: utf-8 -*-
"""neural_style_transfer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iL5WdphxKFVSmSWJH6X7-kFqvVkUG8z9
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.applications import VGG19
from tensorflow.keras.models import Model
from tensorflow.keras import mixed_precision

# Set Matplotlib backend to Agg
import matplotlib
matplotlib.use('Agg')

# Enable mixed precision
mixed_precision.set_global_policy('mixed_float16')

# Load and preprocess images
def load_img(img_path, shape):
    img = tf.io.read_file(img_path)
    img = tf.image.decode_image(img, channels=3, dtype=tf.float32)
    img = tf.image.resize(img, shape)
    img = tf.keras.applications.vgg19.preprocess_input(img * 255.0)
    img = tf.expand_dims(img, axis=0)
    return img

# Display image
def display_img(img, title=None):
    img = tf.squeeze(img, axis=0)
    img = img + [103.939, 116.779, 123.68]
    img = tf.clip_by_value(img, 0.0, 255.0)
    img = tf.cast(img, tf.uint8)
    plt.imshow(img.numpy())
    if title:
        plt.title(title)
    plt.axis('off')
    plt.show()

# Load VGG19 model and extract features
def vgg19(layer_names):
    vgg = VGG19(weights='imagenet', include_top=False)
    vgg.trainable = False
    outputs = [vgg.get_layer(name).output for name in layer_names]
    model = Model([vgg.input], outputs)
    return model

# Define style and content layers
c_layers = ['block5_conv2']
s_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
num_c_layers = len(c_layers)
num_s_layers = len(s_layers)

# Initialize the model for style and content extraction
img_model = vgg19(s_layers + c_layers)

# Get feature representations
def representations(model, c_path, s_path, shape):
    c_image = load_img(c_path, shape)
    s_image = load_img(s_path, shape)

    c_image = tf.cast(c_image, tf.float16)  # Cast to float16
    s_image = tf.cast(s_image, tf.float16)  # Cast to float16

    c_outputs = model(c_image)
    s_outputs = model(s_image)

    c_features = [tf.cast(c_outputs[i], tf.float32) for i in range(num_s_layers, num_s_layers + num_c_layers)]
    s_features = [tf.cast(s_outputs[i], tf.float32) for i in range(num_s_layers)]

    return s_features, c_features

# Compute Gram matrix
def gram_matrix(input_tensor):
    result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
    num_locations = tf.cast(tf.shape(input_tensor)[1] * tf.shape(input_tensor)[2], tf.float32)
    return result / num_locations

# Define loss functions
def compute_s_loss(outputs, targets):
    return tf.add_n([tf.reduce_mean((output - target)**2) for output, target in zip(outputs, targets)]) / num_s_layers

def compute_c_loss(output, target):
    return tf.reduce_mean((output - target)**2)

# Total loss
def compute_loss(model, loss_weights, init_image, gram_style_features, c_features):
    s_weight, c_weight = loss_weights
    model_outputs = model(tf.cast(init_image, tf.float16))  # Cast to float16

    s_output_features = [tf.cast(feature, tf.float32) for feature in model_outputs[:num_s_layers]]
    c_output_features = [tf.cast(feature, tf.float32) for feature in model_outputs[num_s_layers:]]

    s_score = compute_s_loss([gram_matrix(output) for output in s_output_features], gram_style_features)
    c_score = compute_c_loss(c_output_features[0], c_features[0])

    s_score *= s_weight
    c_score *= c_weight

    loss = s_score + c_score
    return loss, s_score, c_score

# Compute gradients
def compute_gradients(config):
    with tf.GradientTape() as tape:
        loss, s_score, c_score = compute_loss(**config)
    total_loss = loss
    return tape.gradient(total_loss, config['init_image']), loss, s_score, c_score

# Style transfer function
def style_transfer(c_path, s_path, shape, num_iterations=3200, s_weight=1e-2, c_weight=1e-2):
    model = img_model
    s_features, c_features = representations(model, c_path, s_path, shape)
    gram_style_features = [gram_matrix(s_feature) for s_feature in s_features]

    init_image = load_img(c_path, shape)
    init_image = tf.Variable(tf.cast(init_image, tf.float32))

    optimizer = tf.optimizers.Adam(learning_rate=5.0, beta_1=0.99, epsilon=1e-1)

    best_loss, best_img = float('inf'), None
    loss_weights = (s_weight, c_weight)

    config = {
        'model': model,
        'loss_weights': loss_weights,
        'init_image': init_image,
        'gram_style_features': gram_style_features,
        'c_features': c_features
    }

    norm_means = np.array([103.939, 116.779, 123.68])
    min_vals = -norm_means
    max_vals = 255.0 - norm_means

    for i in range(num_iterations):
        grads, loss, s_score, c_score = compute_gradients(config)
        optimizer.apply_gradients([(grads, init_image)])
        init_image.assign(tf.clip_by_value(init_image, min_vals, max_vals))

        if loss < best_loss:
            best_loss = loss
            best_img = init_image.numpy()

        if i % 100 == 0:
            print(f"Iteration {i}: Total loss: {loss:.4e}, Style loss: {s_score:.4e}, Content loss: {c_score:.4e}")

    return best_img, best_loss

# Style transfer execution
c_path = "/content/golden-retriever-sitting-down-in-a-farm-837898820-5c7854ff46e0fb00011bf29a.jpg"
s_path = "/content/Street-Modern-painting.jpg"
shape = (512, 512)

final_img, final_loss = style_transfer(c_path, s_path, shape)

display_img(final_img, title="Output Image")

# Save the final image
output_path = "/content/output_image.jpg"
final_img = tf.squeeze(final_img, axis=0)
final_img = tf.image.convert_image_dtype(final_img, dtype=tf.uint8)
tf.io.write_file(output_path, tf.image.encode_jpeg(final_img))

print(f"Output image saved at {output_path}")