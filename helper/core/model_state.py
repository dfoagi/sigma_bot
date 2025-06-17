_current_model = "gemini-2.5-flash-preview-05-20"


def get_current_model():
    return _current_model


def set_current_model(new_model: str):
    global _current_model
    _current_model = new_model
