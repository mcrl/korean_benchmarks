def doc_to_text(doc):
    idx = doc["text"].index("_")
    return doc["text"][:idx].rstrip()


def doc_to_target(doc):
    return 0


def doc_to_choice(doc):
    idx = doc["text"].index("_") + 1
    suffix = doc["text"][idx:]
    options = [doc["answer"], doc["candidate"]]
    return [f"{opt}{suffix}" for opt in options]
