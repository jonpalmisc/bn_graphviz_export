from binaryninja import Settings

KEY_DOT_PATH = "plugin.graphviz.dotPath"
KEY_DEFAULT_FONT = "plugin.graphviz.defaultFont"
KEY_DEFAULT_FONT_SIZE = "plugin.graphviz.defaultFontSize"
KEY_DPI = "plugin.graphviz.dpi"


def register():
    settings = Settings()
    settings.register_setting(
        KEY_DOT_PATH,
        """
        {
            "type": "string",
            "optional": false,
            "title": "DOT Executable Path", 
            "description": "Path to Graphviz's DOT executable.",
            "default": "/usr/local/bin/dot"
        }
        """,
    )
    settings.register_setting(
        KEY_DEFAULT_FONT,
        """
        {
            "type": "string",
            "optional": false,
            "title": "Default Font", 
            "description": "Default font to use in graph nodes.",
            "default": "Courier"
        }
        """,
    )
    settings.register_setting(
        KEY_DEFAULT_FONT_SIZE,
        """
        {
            "type": "number",
            "optional": false,
            "title": "Default Font Size", 
            "description": "Default font size to use in graph nodes.",
            "default": 10,
            "minValue": 8,
            "maxValue": 40
        }
        """,
    )
    settings.register_setting(
        KEY_DPI,
        """
        {
            "type": "number",
            "optional": false,
            "title": "Raster DPI", 
            "description": "DPI to use for generated raster images.",
            "default": 150,
            "minValue": 72,
            "maxValue": 300
        }
        """,
    )


def dot_executable_path() -> str:
    return Settings().get_string(KEY_DOT_PATH)  # pyright: ignore


def default_font() -> str:
    return Settings().get_string(KEY_DEFAULT_FONT)  # pyright: ignore


def default_font_size() -> int:
    return Settings().get_integer(KEY_DEFAULT_FONT_SIZE)  # pyright: ignore


def raster_dpi() -> int:
    return Settings().get_integer(KEY_DPI)  # pyright: ignore
