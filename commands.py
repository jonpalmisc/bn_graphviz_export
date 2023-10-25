from .dialog import ExportDialog

from binaryninja import BinaryView, Function, PluginCommand


def _export(_: BinaryView, function: Function):
    ExportDialog(function).exec()


def register():
    PluginCommand.register_for_function("Graphviz\\Export...", "", _export)
