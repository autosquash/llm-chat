from src.domain import Model


class ModelWrapper:
    """Mutable class to hold current model inside"""

    __slots__ = ("model",)

    model: Model | None

    def __init__(self, model: Model | None = None):
        self.model = model

    def change(self, model: Model) -> None:
        self.model = model
