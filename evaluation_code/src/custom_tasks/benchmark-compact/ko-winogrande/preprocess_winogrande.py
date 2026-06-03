def doc_to_text(doc):
    idx = doc["sentence"].index("_")
    return doc["sentence"][:idx].rstrip()


def doc_to_target(doc):
    answer_to_num = {"1": 0, "2": 1, 1: 0, 2: 1}
    return answer_to_num[doc["answer"]]


def doc_to_choice(doc):
    idx = doc["sentence"].index("_") + 1
    suffix = doc["sentence"][idx:]
    options = [doc["option1"], doc["option2"]]
    return [f"{opt}{suffix}" for opt in options]
