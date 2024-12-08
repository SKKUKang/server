from score import calculate_total_score, time_to_minutes
from timetable_parser import Subject, get_building

def format_time_in_korean(time):
    hours = time // 100
    minutes = time % 100
    return f"{hours}시 {minutes}분"

def adjust_start_time_to_full_or_half_hour(time):
    time= int(time)
    hours = time // 100
    minutes = time % 100
    if minutes < 30:
        return hours * 100  # 정각
    else:
        return hours * 100 + 30  # 30분

def find_best_slot(subject_arr,first,second,third):
    data = {'월': [], '화': [], '수': [], '목': [], '금': []}
    sorted_subjects = sorted(subject_arr, key=lambda x: (x[0], x[2]))
    for lecture in sorted_subjects:  
        day = lecture[0]
        name = lecture[1]
        start_time = lecture[2]
        end_time = lecture[3]
        building = get_building(lecture[4]) 
        data[day].append(Subject(day, name, start_time, end_time, building))  

    best_score = int('-99999999999999999')
    best_slot = None
    new_class_duration = 75  # 새 수업 시간 (75분)

    for day in data:
        subjects = data[day]

        # 공강일 처리
        if not subjects:
            start = int(adjust_start_time_to_full_or_half_hour(800))
            end = 1800 
            while start + new_class_duration <= end:
                end_time = start + (new_class_duration // 60) * 100 + (new_class_duration % 60)
                if int(end_time) % 100 >= 60:
                    end_time += 40

                temp_subject = Subject(day, "New Class", start, end_time, "임시 건물")
                temp_data = {key: value[:] for key, value in data.items()}
                temp_data[day].append(temp_subject)
                temp_data[day].sort(key=lambda x: x.start_time)

                score = calculate_total_score(temp_data,first,second,third)
                if score > best_score:
                    best_score = score
                    best_slot = (day, start, end_time)

                start += 100 if start % 100 == 0 else 70  # 정각/30분 증가
            continue

        # 빈 시간대 탐색
        for i in range(len(subjects) + 1):
            if i == 0:
                start = adjust_start_time_to_full_or_half_hour(800)
                end = time_to_minutes(subjects[0].start_time)
            elif i == len(subjects):
                start = time_to_minutes(subjects[-1].end_time)
                end = 1800
            else:
                start = time_to_minutes(subjects[i - 1].end_time)
                end = time_to_minutes(subjects[i].start_time)

            start += 10
            end -= 10

            while start + new_class_duration <= end:
                start = adjust_start_time_to_full_or_half_hour(start)
                end_time = start + (new_class_duration // 60) * 100 + (new_class_duration % 60)
                if end_time % 100 >= 60:
                    end_time += 40

                temp_subject = Subject(day, "New Class", start, end_time, "임시 건물")
                temp_data = {key: value[:] for key, value in data.items()}
                temp_data[day].append(temp_subject)
                temp_data[day].sort(key=lambda x: x.start_time)

                score = calculate_total_score(temp_data,first,second,third)
                if score > best_score:
                    best_score = score
                    best_slot = (day, start, end_time)

                start += 100 if start % 100 == 0 else 70  

    if best_slot:
        return best_slot
    else:
        best_slot="No available slot"
        return best_slot

