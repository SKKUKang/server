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

# 설문 데이터를 저장할 변수 (임시 저장소)
survey_responses = {}
analysis_results = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/process', methods=['POST'])
def process_request():
    try:
        if 'file' in request.files:
            file = request.files['file']
            filepath = None
            try:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    result = process_image(filepath)  # 이미지 처리
                    analysis_results['Analysis'] = result  # 분석 결과 저장
                    return jsonify({"status": "success", "data": result})
            except Exception as e:
                print(f"Error: {e.strerror}")
                return jsonify({"status": "error", "message": "Invalid file type"}), 400
            finally:
                if filepath and os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except OSError as e:
                        print(f"Error removing file: {e.strerror}")
        elif request.is_json and 'url' in request.json:
            url = request.json.get('url')
            if url:
                result = crawl_subject_texts(url)  # URL 크롤링
                analysis_results['Analysis'] = result  # 분석 결과 저장
                return jsonify({"status": "success", "data": result})
            return jsonify({"status": "error", "message": "Invalid URL"}), 400

        return jsonify({"status": "error", "message": "No valid input provided"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def survey_response():
    try:
        if request.is_json:
            # 설문 데이터를 받음
            data = request.json
            if 'surveyAnswers' in data:
                survey_answers = data['surveyAnswers']
                survey_responses['surveyAnswers'] = survey_answers  # 임시 저장
                print(f"Received survey data: {survey_answers}")
                
                # 처리된 데이터를 기반으로 응답
                return jsonify({"status": "success", "message": "Survey data received successfully"})
            else:
                return jsonify({"status": "error", "message": "Survey answers missing"}), 400
        return jsonify({"status": "error", "message": "Invalid input format"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/result', methods=['GET'])
def get_result():
    try:
        # 설문 응답과 분석 데이터를 결합하여 반환
        result = {
            "survey": survey_responses.get('surveyAnswers', {}),
            "analysis": analysis_results.get('Analysis', {}),
        }
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
