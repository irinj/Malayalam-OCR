from flask import Flask, request, jsonify, send_from_directory
import os
from Segmentation.segment import segment
from Classifier.classify import getLabels
from Unicode.generator import generate

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    try:
        segment(image_path)
        labels, overall_confidence = getLabels()  # Make sure this returns confidence
        generate(labels)

        output_file = os.path.join(os.getcwd(), "output.txt")
        with open(output_file, 'r', encoding='utf-8') as f:
            text = f.read()

        return jsonify({
            'text': text,
            'confidence': float(overall_confidence),  # Add confidence to response
            'download_url': f'/download/{os.path.basename(output_file)}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the uploaded image file
        if os.path.exists(image_path):
            os.remove(image_path)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(debug=True)