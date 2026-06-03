import hashlib


def _ordered_options(doc):
    options = [(doc["answer"], True), (doc["candidate"], False)]
    digest = hashlib.md5(doc["text"].encode("utf-8")).hexdigest()
    if int(digest, 16) % 2:
        options.reverse()
    return options


def doc_to_text(doc):
    options = _ordered_options(doc)
    return (
        "문장의 빈칸에 들어갈 말로 더 자연스러운 선택지를 고르세요.\n"
        f"문장: {doc['text']}\n"
        f"A. {options[0][0]}\n"
        f"B. {options[1][0]}\n"
        "반드시 A 또는 B 중 하나의 문자로만 답하세요.\n"
        "정답:"
    )


def doc_to_target(doc):
    options = _ordered_options(doc)
    return "A" if options[0][1] else "B"
