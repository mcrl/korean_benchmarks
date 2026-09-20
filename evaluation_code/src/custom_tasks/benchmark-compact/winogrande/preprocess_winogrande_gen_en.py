def doc_to_text(doc):
    return (
        "Choose the option that more naturally fills in the blank.\n"
        f"Sentence: {doc['sentence']}\n"
        f"A. {doc['option1']}\n"
        f"B. {doc['option2']}\n"
        "Answer with only the letter A or B.\n"
        "Answer:"
    )


def doc_to_target(doc):
    answer_to_label = {"1": "A", "2": "B", 1: "A", 2: "B"}
    return answer_to_label[doc["answer"]]
