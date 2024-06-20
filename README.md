# Neural_style_transfer
Neural Style Transfer with TensorFlow: Apply artistic styles to images using deep learning. This project demonstrates how to blend the content of one image with the style of another using a VGG19-based model.

#installation Instructions

git clone https://github.com/Damnaki/neural-style-transfer.git
cd neural-style-transfer

# Env Setup
python -m venv venv 
source venv/scripts/activate

# Install libraries
pip install tensorflow matplotlib numpy

# Usage
1. Open the jupyter notebook
   jupyter notebook code/neural_style_transfer.ipynb
2. Run the cells to perform neural style transfer and generate the output image. The notebook includes explanations and steps to guide you through the process.

# Dependencies
The project requires the following libraries:

TensorFlow: pip install tensorflow
NumPy: pip install numpy
Matplotlib: pip install matplotlib

# Code explanation
## Load and Preprocess Images
The function load_img loads and preprocesses the images, resizing them to the desired shape and preparing them for the VGG19 model.

## Display Image
The function display_img displays the processed images.

## VGG19 Model
The function vgg19 loads the VGG19 model and extracts the specified layers for style and content representation.

## Feature Extraction
The function representations extracts the style and content features from the given images using the VGG19 model.

## Gram Matrix
The function gram_matrix computes the Gram matrix, which is used to capture style information from the style image.

## Loss Functions
The functions compute_s_loss and compute_c_loss calculate the style and content losses, respectively. The function compute_loss computes the total loss.

## Gradient Computation
The function compute_gradients computes the gradients required for optimizing the image.

## Style Transfer Function
The function style_transfer performs the style transfer by optimizing the input image to minimize the total loss.

## Execution
Finally, the script performs the style transfer using the provided content and style images, and saves the output image.
