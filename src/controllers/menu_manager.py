from dataclasses import dataclass

from rich.console import Console
from rich.markdown import Markdown

from src.io_helpers import get_input, show_error_msg


class ActionName:
    SALIR = "SALIR"
    CHANGE_MODEL = "CHANGE_MODEL"
    NEW_QUERY = "NEW_QUERY"
    DEBUG = "DEBUG"


@dataclass
class Action:
    name: str


class MenuManager:

    @staticmethod
    def enter_inner_menu(raw_question: str) -> Action | None:

        match raw_question.strip().split():
            case ["/q", *_] | ["/quit", *_] | ["/exit", *_]:
                return Action(ActionName.SALIR)
            case ["/d", *_] | ["/debug", *_]:
                return Action(ActionName.DEBUG)
            case ["/h", *_] | ["/help", *_]:
                MenuManager.show_help()
                get_input("Pulsa Enter para continuar")
                return Action(ActionName.NEW_QUERY)

            case ["/change", *_]:
                return Action(ActionName.CHANGE_MODEL)
            case [other, *_]:
                if other.startswith("/"):
                    show_error_msg("Entrada no válida")
                else:
                    return None
            case _:
                return None

    @staticmethod
    def show_help():
        console = Console()
        markdown = Markdown(
            """
## Consultas
Puedes usar placeholders con el formato `$0<nombre>`. Ejemplo: `¿Quién fue $0persona y que hizo en el ámbito de $0tema?` El programa te pedirá luego que completes los placeholders uno por uno.
Si empiezas el contenido de un placeholder con `/for` y pones las variantes separadas por comas, se generará una consulta con cada variante. Por ejemplo, si en la pregunta anterior introduces como valor de $0persona `/for Alexander Flemming,Albert Einstein` se generarán 2 consultas, una para cada nombre introducido.
### Comandos
Puedes iniciar tu consulta con `/d` para activar el modo depuración.
"""
        )
        console.print(markdown, width=60)
