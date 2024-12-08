import re

def extract_numbers(style):
    # 정규 표현식을 사용하여 숫자 값을 추출
    height_match = re.search(r'height:\s*(\d+)px', style)
    top_match = re.search(r'top:\s*(\d+)px', style)
    
    height = int(height_match.group(1)) if height_match else None
    top = int(top_match.group(1)) if top_match else None
    
    startTimeHour = (top//50)
    startTimeminute= ((top%50)//4)*5
    startTime=startTimeHour*100 + startTimeminute
    duringhour = (height-1)//50
    duringminute = ((height-(duringhour*50+1))//4)*5
    carry = (duringminute + startTimeminute)//60
    endTimeHour=startTimeHour+duringhour+carry
    endTimeminute=(startTimeminute+duringminute)%60
    endTime=endTimeHour*100+endTimeminute
    return int(startTime),int(endTime)

def processing(json_data):
    # 각 json_data에서 객체의 2번째 값인 시간:style을 추출하여 다른 형태로 변형하기
    result = []
    a = 0
    for subject in json_data:
        style = subject.get("시간", "No style attribute")  # 시간:style
        startTime,endTime = extract_numbers(style)
        day = subject.get("요일", "No day")
        course_name = subject.get("과목명", "No course name")
        classroom = subject.get("강의실", "No classroom")
        result.append([day, course_name, startTime, endTime, classroom])
    return result

# 4px 5분
# 8px 10분
# 13px 15분
# 17px 20분
# 21px 25분
# 25px 30분
# 29px 35분
# 33px 40분
# 38px 45분
# 42px 50분
# 46px 55분