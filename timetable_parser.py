class Subject:
    def __init__(self, day, name, start_time, end_time, building):
        self.day = day
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.building = building

    def __str__(self):
        return '과목명 : {0}\n시간: {1}-{2}\n건물: {3}\n'.format(self.name, self.start_time, self.end_time, self.building)


def get_building(lecture_room):
    room_str = str(lecture_room)
    if room_str.startswith("9") and room_str[1].isalpha():
        building_code = "9"  # 국제관
    else:
        building_code = room_str[:2]

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
