def doc_to_text(doc):
    text = "질문: " + doc["question"] + "\n"
    for i, choice in enumerate(doc["choices"]["text"]):
        text += chr(65 + i) + ". " + choice + "\n"
    return text + "반드시 A, B, C, D 중 하나의 문자로만 답하세요.\n정답:"


def doc_to_target(doc):
    labels = doc["choices"]["label"]
    answer_idx = labels.index(doc["answerKey"])
    return chr(65 + answer_idx)
