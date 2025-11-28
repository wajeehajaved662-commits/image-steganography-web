# Image Steganography Web App

## Overview
This project is a web-based application built using **Python** and **FastAPI** that allows users to hide and reveal secret messages inside images using **Least Significant Bit (LSB) steganography**. It provides an interactive and easy-to-use interface where users can encode messages into images and decode them back, all from their web browser.  

## Features
- **Encode Secret Messages**: Hide a secret text message in any PNG image.
- **Decode Messages**: Retrieve hidden messages from encoded images.
- **Interactive Web Interface**: Upload images and view results instantly.
- **Cross-Platform**: Works on Windows, Linux, and Mac.
- **Secure Encoding**: Uses LSB method to safely hide messages without noticeable changes to the image.

## Technologies Used
- **Python 3.x**: Core programming language
- **FastAPI**: Backend web framework for API handling
- **Pillow (PIL)**: Image processing
- **NumPy**: Array and bit manipulation
- **HTML, CSS, JavaScript**: Frontend interface
- **UVicorn**: ASGI server to run FastAPI apps

## How It Works
1. The user selects an image to encode a secret message.
2. The message is converted to binary and embedded into the image's pixel data using the **LSB technique**.
3. The encoded image can be downloaded directly from the browser.
4. For decoding, the user uploads the encoded image.
5. The hidden message is extracted from the image pixel data and displayed.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stego-web-app.git
