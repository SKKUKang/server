import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
import os

class TimetableExtractor:
    def __init__(self, image_file):
        # 시간표 이미지
        self.image_file = cv2.imread(image_file)
        self.width = self.image_file.shape[1]

        # 요일별로 이미지를 저장할 딕셔너리
        self.cropped_images = {'월': [], '화': [], '수': [], '목': [], '금': []}
        self.days = ['월', '화', '수', '목', '금']  # 딕셔너리 저장을 도울 리스트

        # 색상 범위 정의(HSV)
        self.color_ranges = {
            "파랑": ([100, 100, 100], [130, 255, 255]),
            "보라": ([130, 100, 100], [160, 255, 255]),
            "주황": ([10, 100, 150], [19, 255, 255]),
            "연두": ([40, 100, 100], [70, 255, 255]),
            "빨강": ([0, 100, 100], [9, 255, 255]),
            "노랑": ([20, 100, 100], [39, 255, 255]),
            "청록": ([80, 100, 100], [100, 255, 255])
        }

        self.result = []  # 최종 데이터 저장 리스트
        self.time_dict = {}  # 시간 매핑 딕셔너리

    def getlectrue(self):
        hsv = cv2.cvtColor(self.image_file, cv2.COLOR_BGR2HSV)
        for color_name, (lower, upper) in self.color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)

            # 색상 마스크 생성
            mask = cv2.inRange(hsv, lower, upper)

            # 마스크를 팽창하여 블록을 더 명확히
            mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)

            # 윤곽선 찾기
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 윤곽선에 따라 이미지 잘라내기
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 50:
                    cropped_image = self.image_file[y:y+h, x:x+w]
                    self.cropped_images[self.days[int(x/self.width*5)]].append(
                        [Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)), y, y+h]
                    )

    def get_pixel_per_hour(self):
        left_image = self.image_file[:, :int(self.width * 0.1)]
        gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]
        custom_config = r'--oem 3 --psm 6'
        text_data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

        count = 0
        time_y_positions = []
        for i, text in enumerate(text_data['text']):
            if text.strip().isdigit() and int(text) >= 9 and int(text) <= 12 and count < 2:
                time_y_positions.append(text_data['top'][i])
                count += 1

        return abs(time_y_positions[1] - time_y_positions[0]), time_y_positions[0]

    def get_time_dictionary(self):
        pixel_per_hour, start_y_position = self.get_pixel_per_hour()
        time_interval = 15
        intervals_per_hour = 60 // time_interval
        pixels_per_interval = pixel_per_hour / intervals_per_hour
        current_y_position = start_y_position
        current_hour = 9
        current_minute = 0

        while current_hour < 24:
            time_str = f"{current_hour:02}{current_minute:02}"
            self.time_dict[int(current_y_position)] = time_str
            current_minute += time_interval
            if current_minute == 60:
                current_minute = 0
                current_hour += 1
            current_y_position += pixels_per_interval

    def save_lecture_data(self):
        if not self.time_dict:
            self.get_time_dictionary()

        for day in self.days:
            for image, y, y_end in self.cropped_images[day]:
                gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
                _, inverted = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                text = pytesseract.image_to_string(inverted, config='--psm 6 -l kor').strip()
                start_y = min(self.time_dict.keys(), key=lambda key: abs(key - y))
                end_y = min(self.time_dict.keys(), key=lambda key: abs(key - y_end))
                start_time = self.time_dict[start_y]
                end_time = self.time_dict[end_y]

                text = text.replace('\n', '').replace(' ', '')
                match = re.search(r'\d', text)
                course_name = text[:match.start()] if match else text
                course_number = text[match.start():] if match else ''
                self.result.append([day, course_name, start_time, end_time, course_number])


def process_image(image_path):
    # Tesseract 경로 설정
    base_dir = os.path.dirname(__file__)
    pytesseract.pytesseract.tesseract_cmd = os.path.join(base_dir, "Tesseract-OCR", "tesseract.exe")
    os.environ["TESSDATA_PREFIX"] = os.path.join(base_dir, "Tesseract-OCR","tessdata")

    # 이미지 처리
    extractor = TimetableExtractor(image_path)
    extractor.getlectrue()
    extractor.get_time_dictionary()
    extractor.save_lecture_data()
    return extractor.result



