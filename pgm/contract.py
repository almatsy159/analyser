import os
import io
# --------------------------
# Structures for each direction
# --------------------------
ui_to_handler_data = {
    "process": str,
    "sid": int,
    "cid": int
}
ui_to_handler_file = {
    "image": (os.PathLike,io.BytesIO,str)
}

handler_to_ui = {
    "status": str,
    "result": dict,
    "sid": int
}

class ContentStructure:
    def __init__(self, content, structure):
        self.content = content
        self.structure = structure
        self.extracted = {}
        self.validate_data()

    def validate_data(self):
        missing_keys = [k for k in self.structure if k not in self.content]
        if missing_keys:
            raise KeyError(f"Missing keys: {missing_keys}")

        extra_keys = [k for k in self.content if k not in self.structure]
        if extra_keys:
            raise KeyError(f"Unexpected keys: {extra_keys}")

        for key, expected_type in self.structure.items():
            value = self.content[key]
            if not isinstance(value, expected_type):
                raise TypeError(f"Key '{key}' expects {expected_type.__name__}, got {type(value).__name__}")
            setattr(self, key, value)
            self.extracted[key] = value

# --------------------------
# Direction-specific wrappers
# --------------------------
class UI_to_Handler_Data(ContentStructure):
    def __init__(self, content):
        super().__init__(content, ui_to_handler_data)

class UI_to_Handler_File(ContentStructure):
    def __init__(self, content):
        super().__init__(content, ui_to_handler_file)
class Handler_to_UI(ContentStructure):
    def __init__(self, content):
        super().__init__(content, handler_to_ui)