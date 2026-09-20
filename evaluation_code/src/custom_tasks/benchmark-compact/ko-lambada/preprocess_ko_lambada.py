def doc_to_text(doc):
    # return 0
  
    idx = doc["text"].index("_")
    return doc["text"][:idx].rstrip()


def doc_to_target(doc):
    # idx = doc["text"].index("_") + 1
    # return doc["text"][idx:].strip()

    return 0


def doc_to_choice(doc):
    # idx = doc["text"].index("_")
    # options = [doc["answer"], doc["candidate"]]
    # return [doc["text"][:idx] + opt for opt in options]

    idx = doc["text"].index("_") + 1
    suffix = doc["text"][idx:]
    options = [doc["answer"], doc["candidate"]]
    return [f"{opt}{suffix}" for opt in options]
