from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from ocr import process_image
from webcroll import crawl_subject_texts
from flask_cors import CORS
import shutil
import time
from best_slot import find_best_slot

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 모든 도메인 허용

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 설문 데이터와 분석 결과를 저장할 딕셔너리 (requestId 기반 저장)
survey_responses = {}
analysis_results = {}
etc = {}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/process', methods=['POST'])
def process_request():
    try:
        # requestId를 요청에서 가져옴
        request_id = request.form.get('requestId') or request.json.get('requestId')
        if not request_id:
            return jsonify({"status": "error", "message": "Missing requestId"}), 400
# 파일 업로드 처리
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], request_id)  # 생성된 폴더 경로
                filepath = os.path.join(folder_path, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                try:
                    result = process_image(filepath)  # 이미지 처리
                    analysis_results[request_id] = {"analysis": result}  # requestId로 저장
                    return jsonify({"status": "success", "data": result})
                finally:
                    # 업로드 시 생성된 폴더 삭제
                    if os.path.exists(folder_path):
                        try:
                            shutil.rmtree(folder_path)  # 해당 폴더 및 하위 파일 삭제
                        except Exception as e:
                            print(f"Error cleaning up folder {folder_path}: {e}")
        # URL 처리
        elif request.is_json and 'url' in request.json:
            url = request.json.get('url')
            if url:
                result = crawl_subject_texts(url)  # URL 크롤링
                analysis_results[request_id] = {"analysis": result}  # requestId로 저장
                return jsonify({"status": "success", "data": result})
            return jsonify({"status": "error", "message": "Invalid URL"}), 400

        return jsonify({"status": "error", "message": "No valid input provided"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def survey_response():
    try:
        # requestId를 요청에서 가져옴
        request_id = request.json.get('requestId')
        if not request_id:
            return jsonify({"status": "error", "message": "Missing requestId"}), 400
        # 설문 데이터를 저장
        if request.is_json and 'surveyAnswers' in request.json:
            survey_responses[request_id] = request.json['surveyAnswers']  # requestId로 저장
            etc[request_id] = analysis_results[request_id]["analysis"]  # requestId로 저장
            return jsonify({"status": "success", "message": "Survey data received successfully"})
        return jsonify({"status": "error", "message": "Survey answers missing"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/result', methods=['GET'])
def get_result():
    try:
        # requestId를 요청에서 가져옴
        request_id = request.args.get('requestId')
        if not request_id:
            return jsonify({"status": "error", "message": "Missing requestId"}), 400

        # 결과를 조회할 때까지 대기
        timeout = 30  # 최대 대기 시간 (초)
        wait_time = 1   # 상태 체크 간격 (초)
        elapsed_time = 0
        
        while elapsed_time < timeout:
            # requestId 기반으로 결과 조회
            totalresult = {
                "survey": survey_responses.get(request_id, {}),
                "analysis": analysis_results.get(request_id, {}).get("analysis", {}),
                "etc": etc.get(request_id, {})
            }

            # 분석이 준비되었으면 결과 반환
            if totalresult["survey"] and totalresult["analysis"] and totalresult["etc"]:
                return jsonify({"status": "success", "data": totalresult})

            # 분석이 준비되지 않았으면 대기 후 재시도
            time.sleep(wait_time)
            elapsed_time += wait_time

        # timeout이 지나면 분석 결과가 없다는 응답
        return jsonify({"status": "error", "message": "Analysis result not ready after waiting"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "Welcome to the 복학왕조!"



if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8080, debug=False)

