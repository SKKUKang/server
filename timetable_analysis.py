from timetable_parser import Subject
from score import time_to_minutes

def convert_to_dict(data):
    timetable = {'월': [], '화': [], '수': [], '목': [], '금': []}
    for entry in data:
        day, name, start_time, end_time, building = entry
        timetable[day].append(
            Subject(
                day,
                name,
                int(start_time),  
                int(end_time),    #
                building
            )
        )
    return timetable


def analyze_timetable(data):
    features = {
        "아침형 인간": False,
        "저녁형 인간": False,
        "베짱이": False,
        "공강 마스터": False,
        "건물 여행자": False,
        "연강 마스터": False,
        "마라토너": False,
        "오후만 출근족": False,
    }

    total_classes = 0
    morning_days = 0
    evening_days = 0
    free_days = 0
    marathon_days = 0
    afternoon_only_days = 0
    travel_days = 0
    intense_days = 0

    for day, subjects in data.items():
        if not subjects:
            free_days += 1  
            continue

        # 초기화
        daily_minutes = 0
        buildings = set()
        continuous_count = 0
        morning_class = False
        evening_class = False
        afternoon_only = True
        last_end_time = None

        for i, subject in enumerate(subjects):
            total_classes += 1
            buildings.add(subject.building)
            daily_minutes += time_to_minutes(subject.end_time) - time_to_minutes(subject.start_time)

            # 아침형 인간
            if subject.start_time == 900:
                morning_class = True

            # 저녁형 인간
            if subject.start_time >= 1700:
                evening_class = True

            # 오후만 출근족
            if subject.start_time < 1200:
                afternoon_only = False

            # 연강
            if i > 0 and last_end_time is not None:
                gap = time_to_minutes(subject.start_time) - time_to_minutes(last_end_time)
                if gap <= 15:
                    continuous_count += 1
                else:
                    continuous_count = 0

            last_end_time = subject.end_time

        if morning_class:
            morning_days += 1
        if evening_class:
            evening_days += 1
        if afternoon_only:
            afternoon_only_days += 1
        if daily_minutes >= 300:
            marathon_days += 1
        if len(buildings) >= 3:
            travel_days += 1
        if continuous_count >= 3:
            intense_days += 1

    # 최종 조건 판단
    features["아침형 인간"] = morning_days >= 3
    features["저녁형 인간"] = evening_days >= 3
    features["베짱이"] = total_classes <= 4
    features["공강 마스터"] = free_days >= 2
    features["건물 여행자"] = travel_days >= 2
    features["연강 마스터"] = intense_days >= 2
    features["마라토너"] = marathon_days >= 1
    features["오후만 출근족"] = afternoon_only_days >= 4

    return features
