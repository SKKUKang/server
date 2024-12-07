# score.py

from timetable_parser import Subject, get_building

def print_schedule(data):
    for day, subjects in data.items():
        print(f"--- {day}요일 ---")
        if not subjects:
            print("공강입니다.")
        else:
            for subject in subjects:
                print(subject)


def time_to_minutes(time):
    time = int(time)
    hours = time // 100
    minutes = time % 100
    return int(hours * 60 + minutes)


def find_day_off(data):
    score = 0
    if len(data['월']) == 0:
        score += 10
    if len(data['화']) == 0:
        score += 5
    if len(data['수']) == 0:
        score += 5
    if len(data['목']) == 0:
        score += 5
    if len(data['금']) == 0:
        score += 10
    return score


def find_first_class(data):
    score = 0
    for day in data:
        for subject in data[day]:
            if subject.start_time == 900:
                score -= 5
                break
    return score


def building_route(data):
    building_distance = {
        ("인문관", "경제관"): 1,
        ("인문관", "경영관"): 2,
        ("인문관", "호암관"): 1,
        ("인문관", "수선관"): 3,
        ("인문관", "수선관별관"): 3,
        ("인문관", "국제관"): 5,
        ("인문관", "법학관"): 4,
        ("경제관", "경영관"): 1,
        ("경제관", "호암관"): 1,
        ("경제관", "수선관"): 3,
        ("경제관", "수선관별관"): 3,
        ("경제관", "국제관"): 5,
        ("경제관", "법학관"): 4,
        ("경영관", "호암관"): 1,
        ("경영관", "수선관"): 3,
        ("경영관", "수선관별관"): 3,
        ("경영관", "국제관"): 3,
        ("경영관", "법학관"): 2,
        ("호암관", "수선관"): 3,
        ("호암관", "수선관별관"): 3,
        ("호암관", "국제관"): 3,
        ("호암관", "법학관"): 2,
        ("수선관", "수선관별관"): 1,
        ("수선관", "국제관"): 7,
        ("수선관", "법학관"): 2,
        ("수선관별관", "국제관"): 7,
        ("수선관별관", "법학관"): 2,
        ("국제관", "법학관"): 6,
    }
    total_penalty = 0
    for day, subjects in data.items():
        subjects.sort(key=lambda x: x.start_time)
        for i in range(len(subjects) - 1):
            current = subjects[i]
            next_ = subjects[i + 1]
            current_end = time_to_minutes(current.end_time)
            next_start = time_to_minutes(next_.start_time)
            time_gap = next_start - current_end
            if time_gap <= 15:
                distance_key = (current.building, next_.building)
                penalty = building_distance.get(
                    distance_key, building_distance.get((next_.building, current.building), 0)
                )
                total_penalty -= penalty
    return total_penalty


def check_lunch_time(data):
    total_penalty = 0
    lunch_start = int(time_to_minutes(1100))
    lunch_end = int(time_to_minutes(1400))
    lunch_min_time = 30

    for day, subjects in data.items():
        if not subjects:
            continue
        subjects.sort(key=lambda x: x.start_time)
        first_start = int(time_to_minutes(subjects[0].start_time))
        last_end = int(time_to_minutes(subjects[-1].end_time))

        if first_start >= lunch_start + lunch_min_time:
            continue
        if last_end <= lunch_end - lunch_min_time:
            continue

        lunch_possible = False
        for i in range(len(subjects) - 1):
            current_end = int(time_to_minutes(subjects[i].end_time))
            next_start = int(time_to_minutes(subjects[i + 1].start_time))
            if int(current_end) < int(lunch_end) and next_start > lunch_start and (next_start - current_end) >= lunch_min_time:
                lunch_possible = True
                break
        if not lunch_possible:
            total_penalty -= 5

    return total_penalty


def find_continuous_classes(data):
    total_penalty = 0
    for day, subjects in data.items():
        if not subjects:
            continue
        continuous_count = 0
        for i in range(len(subjects) - 1):
            current_end = int(time_to_minutes(subjects[i].end_time))
            next_start = int(time_to_minutes(subjects[i + 1].start_time))
            gap = next_start - current_end
            if gap > 0 and gap <= 16:
                continuous_count += 1
            else:
                if continuous_count > 2:
                    total_penalty -= (continuous_count - 2) * 5
                continuous_count = 0
        if continuous_count > 2:
            total_penalty -= (continuous_count - 2) * 5
    return total_penalty


def find_evening_classes(data):
    total_penalty = 0
    for day, subjects in data.items():
        for subject in subjects:
            if int(subject.start_time) >= 1800:
                total_penalty -= 5
    return total_penalty


def return_score(subject_arr):
    data = {'월': [], '화': [], '수': [], '목': [], '금': []}
    sorted_subjects = sorted(subject_arr, key=lambda x: (x[0], x[2]))
    for subject in sorted_subjects:
        day = subject[0]
        name = subject[1]
        start_time = subject[2]
        end_time = subject[3]
        building = get_building(subject[4])
        if building == "알 수 없음":
            continue
        data[day].append(Subject(day, name, start_time, end_time, building))

    print_schedule(data)
    total_score = 50
    total_score += find_day_off(data)
    total_score += find_first_class(data)
    total_score += building_route(data)
    total_score += check_lunch_time(data)
    total_score += find_continuous_classes(data)
    total_score += find_evening_classes(data)
    return total_score

def calculate_total_score(data):
    total_score = 50  # 기본 점수
    total_score += find_day_off(data)
    total_score += find_first_class(data)
    total_score += building_route(data)
    total_score += check_lunch_time(data)
    total_score += find_continuous_classes(data)
    total_score += find_evening_classes(data)
    return int(total_score)
