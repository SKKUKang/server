from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from ocr import process_image
from webcroll import crawl_subject_texts
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/process', methods=['POST'])
def process_request():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                result = process_image(filepath)
                return jsonify({"status": "success", "data": result})

            return jsonify({"status": "error", "message": "Invalid file type"}), 400

        elif request.is_json and 'url' in request.json:
            url = request.json.get('url')
            if url:
                result = crawl_subject_texts(url)
                print(result)
                return jsonify({"status": "success", "data": result})
            return jsonify({"status": "error", "message": "Invalid URL"}), 400

        return jsonify({"status": "error", "message": "No valid input provided"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
