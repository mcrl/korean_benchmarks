def doc_to_text(doc):
    text = "Question: " + doc["question"] + "\n"
    for i, choice in enumerate(doc["choices"]["text"]):
        text += chr(65 + i) + ". " + choice + "\n"
    return text + "Answer with only the letter A, B, C, or D.\nAnswer:"


def doc_to_target(doc):
    labels = doc["choices"]["label"]
    answer_idx = labels.index(doc["answerKey"])
    return chr(65 + answer_idx)
