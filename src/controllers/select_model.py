from typing import Final, Sequence

from rich import print

from src.domain import Model, ModelName
from src.models.model_choice import ModelChoiceParser
from src.view import (
    BOLD_STYLE,
    NEUTRAL_MSG,
    Raw,
    SimpleView,
    apply_style_tag,
    escape_for_rich,
    show_error_msg,
    to_styled,
)

INDEX_OF_DEFAULT_MODEL: Final = 0  # pragma: no mutate


class SelectModelController:
    def __init__(self, models: Sequence[Model]) -> None:
        self._model_choice_parser = ModelChoiceParser(models)
        self._models = models
        self._default_model = self._models[INDEX_OF_DEFAULT_MODEL]
        self._view = SimpleView()

    def select_model(self) -> Model:
        """
        Prompt the user to choose a model. Returns the model name without the 'mistral' preffix.
        """
        num_options = len(self._models)
        assert num_options > 0
        chosen_model = None
        while not chosen_model:

            self._show_options()

            user_choice = self._view.get_input(
                apply_style_tag(
                    Raw(f"Introduce tu elección (1-{num_options})"), BOLD_STYLE
                )
            )
            if user_choice:
                try:
                    chosen_model = self._model_choice_parser.parse(user_choice)
                except ValueError as err:
                    show_error_msg(Raw(str(err)))
            else:
                chosen_model = self._default_model

        self._view.print(
            escape_for_rich(Raw(f"\nModelo elegido: {chosen_model.model_name}"))
        )
        return chosen_model

    def _show_options(self) -> None:
        # Mostrar opciones al usuario
        print(
            apply_style_tag(
                Raw(
                    "\nPor favor, elige un modelo introduciendo el número correspondiente:"
                ),
                NEUTRAL_MSG,
            )
        )
        for i, model in enumerate(self._models, start=1):
            self._view.print(escape_for_rich(Raw(f"{i}. {model.model_name}")))

        styled_default_model_explanation = create_styled_default_model_explanation(
            self._default_model.model_name
        )
        print(styled_default_model_explanation)


def create_styled_default_model_explanation(default_model: ModelName) -> str:
    model_name_styled = apply_style_tag(Raw(f"{default_model}"), BOLD_STYLE)
    explanation = to_styled(
        "\nPresiona enter sin seleccionar un número para elegir el modelo "
        + model_name_styled
        + " por defecto."
    )
    return apply_style_tag(explanation, NEUTRAL_MSG)
