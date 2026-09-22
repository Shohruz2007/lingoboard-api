
def calculate_score(student_answers:dict, right_answers:dict):
    score = 0
    for key, value in student_answers.items():
        student_val = value.strip().upper()
        correct = right_answers.get(key)
        if not correct:
            continue
        correct_val = correct.strip().upper()
        if "/" in correct_val:
            options = [ans.strip().upper() for ans in correct_val.split("/")]
            if student_val in options:
                score += 1
        elif student_val == correct_val:
            score += 1
    return f"{score}/{len(right_answers)}" if right_answers else "0/0"

def merge_answer_list_to_dict(answer_list : list) -> dict:
    if not isinstance(answer_list, list):
        raise ValueError("Input must be a list")

    merged = {}
    for item in answer_list:
        if not isinstance(item, dict):
            raise ValueError("Each item must be a dictionary")
        if len(item) != 1:
            raise ValueError("Each dictionary must contain exactly one key-value pair")
        merged.update(item)
    return merged
