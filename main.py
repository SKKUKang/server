# main.py

#from OCR_Timetable import TimetableExtractor
from score import return_score
from best_slot import find_best_slot
from timetable_analysis import analyze_timetable, convert_to_dict

temp= [[
      "월",
      "데이타베이스",
      "1630",
      "1745",
      "50317"
    ],
    [
      "화",
      "웹프로그래밍",
      "1500",
      "1615",
      "50213"
    ],
    [
      "화",
      "네트워크운영관리",
      "1200",
      "1315",
      "50317"
    ],
    [
      "화",
      "특수교육학개론",
      "1000",
      "1145",
      "50106"
    ],
    [
      "화",
      "데이터통신기스술",
      "1330",
      "1445",
      "50317"
    ],
    [
      "수",
      "교육평가",
      "1500",
      "1645",
      "50306"
    ],
    [
      "수",
      "교육의심리학적이해",
      "1100",
      "1245",
      "50104"
    ],
    [
      "목",
      "웹프로그래밍",
      "1630",
      "1745",
      "50213"
    ],
    [
      "목",
      "네트워크운영관리",
      "1330",
      "1445",
      "50213"
    ],
    [
      "목",
      "컴퓨터구조",
      "900",
      "1045",
      "50306"
    ],
    [
      "목",
      "데이터통신기스술",
      "1200",
      "1315",
      "50317"
    ]]

def convert_time_to_int(temp):
    for item in temp:
        # 세 번째 값과 네 번째 값이 문자열로 되어 있으면 정수로 변환
        if isinstance(item[2], str) and item[2].isdigit():
            item[2] = int(item[2])
        if isinstance(item[3], str) and item[3].isdigit():
            item[3] = int(item[3])
    return temp


def main_function(result, first, second, third):
    timetable_dict = convert_to_dict(result)
    result = convert_time_to_int(result)

    # 기존 시간표 점수 계산 및 출력
    print("\n기존 시간표 점수 계산:")
    current_score = return_score(result, first, second, third)
    print(f"기존 시간표 점수: {current_score}")

    # 최적 추가 시간대 계산
    print("\n최적 추가 시간대 계산:")
    best_slot = find_best_slot(result,first,second,third)

    if best_slot:
        print(f"추천 추가 시간: {best_slot[0]}요일 {best_slot[1]}-{best_slot[2]}")
    else:
        print("추가할 최적의 시간대를 찾을 수 없습니다.")

    # 시간표 특징 분석
    print("\n시간표 특징 분석:")
    features = analyze_timetable(timetable_dict)
    return current_score, best_slot, features


#if __name__ == "__main__":
    #main_function(temp)
