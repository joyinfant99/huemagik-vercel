import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting HueMagik backend...")

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {
    "origins": ["http://huemagik.com", "https://huemagik.com", "https://huemagik-frontend.onrender.com", "https://joyinfant99.github.io", 
                "http://localhost:3000"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["Access-Control-Allow-Origin"],
    "supports_credentials": True
}})

def get_colors(image, number_of_colors):
    try:
        image = image.resize((150, 150))
        image = image.convert("RGB")
        image_array = np.array(image)
        image_array = image_array.reshape((image_array.shape[0] * image_array.shape[1], 3))
        kmeans = KMeans(n_clusters=number_of_colors)
        kmeans.fit(image_array)
        colors = kmeans.cluster_centers_
        colors = colors.round().astype(int)
        return colors.tolist()
    except Exception as e:
        logger.error(f"Error in get_colors: {str(e)}")
        logger.error(traceback.format_exc())
        return None

@app.route('/process_image', methods=['POST', 'OPTIONS'])
def process_image():
    logger.info(f"Received request to /process_image. Method: {request.method}")
    if request.method == 'OPTIONS':
        return '', 204
    try:
        if 'image' not in request.files:
            logger.warning("No image file provided in the request")
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        number_of_colors = int(request.form.get('colors', 5))
        
        logger.info(f"Processing image with {number_of_colors} colors")
        
        image = Image.open(image_file)
        colors = get_colors(image, number_of_colors)
        
        if colors is None:
            logger.error("Failed to process image")
            return jsonify({'error': 'Failed to process image'}), 500
        
        logger.info(f"Processed colors: {colors}")
        return jsonify({'colors': colors})
    except Exception as e:
        logger.error(f"Error in process_image: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/')
def home():
    logger.info("Home route accessed")
    return "HueMagik Backend is running successfully!"

@app.route('/test', methods=['GET'])
def test():
    logger.info("Test route accessed")
    return jsonify({'message': 'HueMagik Backend is working!'}), 200

@app.route('/<path:path>')
def catch_all(path):
    logger.warning(f"Undefined route accessed: /{path}")
    return jsonify({'error': f'Undefined route: /{path}'}), 404

@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 Error: {error}")
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}")
    logger.error(traceback.format_exc())
    return jsonify({'error': 'Internal Server Error'}), 500

# Remove the if __name__ == '__main__': block

# Add this line at the end of the file
app = app.wsgi_app