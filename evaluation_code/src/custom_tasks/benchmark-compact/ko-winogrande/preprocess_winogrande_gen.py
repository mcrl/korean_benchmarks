def doc_to_text(doc):
    return (
        "문장의 빈칸에 들어갈 말로 더 자연스러운 선택지를 고르세요.\n"
        f"문장: {doc['sentence']}\n"
        f"A. {doc['option1']}\n"
        f"B. {doc['option2']}\n"
        "반드시 A 또는 B 중 하나의 문자로만 답하세요.\n"
        "정답:"
    )


def doc_to_target(doc):
    answer_to_label = {"1": "A", "2": "B", 1: "A", 2: "B"}
    return answer_to_label[doc["answer"]]
