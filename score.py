# 각 과목 저장 클래스
class Subject:
    def __init__ (self, day, name, start_time, end_time, building):
        self.day = day
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.building = building

    def __str__ (self):
        return '과목명 : {0}\n시간: {1}-{2}\n건물: {3}\n'.format(self.name, self.start_time, self.end_time, self.building)

def get_building(lecture_room):
    # 강의실 번호를 문자열로 변환
    room_str = str(lecture_room)

    # 국제관(9)의 경우, 알파벳이 포함된 강의실 번호 처리
    if room_str.startswith("9") and room_str[1].isalpha():
        building_code = "9"  # 국제관
    else:
        # 일반적인 경우: 앞 두 자리를 건물 코드로 사용
        building_code = room_str[:2]

    # 건물 코드와 이름
    building_map = {
        "31": "인문관",
        "32": "경제관",
        "33": "경영관",
        "50": "호암관",
        "61": "수선관",
        "62": "수선관별관",
        "9": "국제관",
        "2": "법학관"
    }

    return building_map.get(building_code, "알 수 없음")

def print_schedule(data):
    for day, subjects in data.items():
        print(f"--- {day}요일 ---")
        if not subjects:
            print("공강입니다.")
        else:
            for subject in subjects:
                print(subject)  

def time_to_minutes(time):
    hours = time // 100 
    minutes = time % 100  
    return hours * 60 + minutes

def find_day_off(data):
    score = 0 

    if len(data['월']) == 0:
        score += 10
        print(f"월요일 공강 10점 추가")
    if len(data['화']) == 0:
        score += 5
        print(f"화요일 공강 5점 추가")
    if len(data['수']) == 0:
        score += 5
        print(f"수요일 공강 5점 추가")
    if len(data['목']) == 0:
        score += 5
        print(f"목요일 공강 5점 추가")
    if len(data['금']) == 0:
        score += 10
        print(f"금요일 공강 10점 추가")

    return score

def find_first_class(data):
    score = 0  

    for day in data:
        for subject in data[day]:
            if subject.start_time == 900:
                print(f"{day}요일 1교시 수업 {subject.name} 5점 감점")
                score -= 5
                break  

    return score

def building_route(data):
    # 건물 간 거리 점수 매핑
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

    total_penalty = 0  # 총 감점 점수

    for day, subjects in data.items():
        # 수업 시작 시간 순으로 정렬
        subjects.sort(key=lambda x: x.start_time)

        for i in range(len(subjects) - 1):
            current_subject = subjects[i]
            next_subject = subjects[i + 1]

            current_building = current_subject.building
            next_building = next_subject.building

            # 동일 건물은 감점 없음
            if current_building == next_building:
                continue

            # 두 수업 간 시간 간격 계산
            current_end = time_to_minutes(current_subject.end_time)
            next_start = time_to_minutes(next_subject.start_time)
            time_gap = next_start - current_end

            # 시간 간격이 15분 이하일 때만 감점
            if time_gap <= 15:
                distance_key = (current_building, next_building)
                penalty = building_distance.get(distance_key, building_distance.get((next_building, current_building), 0))

                print(f"{day}요일 {current_subject.name} -> {next_subject.name} 이동: {current_building} -> {next_building}, 감점 {penalty}점 (시간 간격: {time_gap}분)")
                total_penalty -= penalty

    return total_penalty


def check_lunch_time(data):

    total_penalty = 0  # 총 감점 점수

    # 점심시간 범위 (분 단위로 변환)
    lunch_start = time_to_minutes(1100)
    lunch_end = time_to_minutes(1400)
    lunch_min_time = 30  # 최소 점심시간 (분)

    for day, subjects in data.items():
        # 공강일은 점심시간을 고려하지 않음
        if not subjects:
            continue

        # 수업을 시작 시간 기준으로 정렬
        subjects.sort(key=lambda x: x.start_time)

        # 첫 수업과 마지막 수업 시간 (분 단위로 변환)
        first_start = time_to_minutes(subjects[0].start_time)
        last_end = time_to_minutes(subjects[-1].end_time)

        # 조건 3: 첫 수업이 점심시간 이후(11:30) 시작하면 점심 가능
        if first_start >= lunch_start + lunch_min_time:
            continue

        # 조건 4: 마지막 수업이 점심시간 이전(13:30) 끝나면 점심 가능
        if last_end <= lunch_end - lunch_min_time:
            continue

        lunch_possible = False  
        for i in range(len(subjects) - 1):
            current_end = time_to_minutes(subjects[i].end_time)
            next_start = time_to_minutes(subjects[i + 1].start_time)

            # 두 수업 사이의 여유 시간 계산
            gap = next_start - current_end
            if current_end < lunch_end and next_start > lunch_start and gap >= lunch_min_time:
                lunch_possible = True
                break

        # 점심시간이 없으면 감점
        if not lunch_possible:
            print(f"{day}요일 점심시간 확보 불가능: 감점 5점")
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
            print(f"'{name}' 과목은 건물을 알 수 없음으로 제외")
            continue

        data[day].append(Subject(day, name, start_time, end_time, building))

    print_schedule(data)
    print()

    total_score = 50

    total_score += find_day_off(data)
    total_score += find_first_class(data)
    total_score += building_route(data)
    total_score += check_lunch_time(data)

    print()
    print("시간표 점수 :", total_score)

    return total_score