_current_model = "gemini-2.5-flash-preview-05-20"
_current_topk = 3


def get_current_model():
    return _current_model


def set_current_model(new_model: str):
    global _current_model
    _current_model = new_model


def get_current_topk():
    return str(_current_topk)


def set_current_topk(new_topk: int):
    global _current_topk
    _current_topk = new_topk
