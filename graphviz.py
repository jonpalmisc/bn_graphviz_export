from binaryninja import (
    AnyFunctionType,
    BasicBlock,
)


def _node_name(block: BasicBlock) -> str:
    if block.is_low_level_il:
        kind = "llil"
    elif block.is_medium_level_il:
        kind = "mlil"
    elif block.is_high_level_il:
        kind = "hlil"
    else:
        kind = "asm"

    return f"{kind}_{block.index}"


def _label_escape(line: str) -> str:
    return line.replace("\\n", "\\\\n").replace('"', '\\"')


def to_dot(
    function: AnyFunctionType, font_name: str = "Courier", font_size: int = 10
) -> str:
    """Generate DOT code to represent a function's control flow graph."""

    NODE_ATTRIBUTES = f'shape=box fontname="{font_name}" fontsize={font_size}'

    nodes = []
    edges = []

    for block in function.basic_blocks:
        lines = [
            f"{line.address:08x}:  {line}" for line in block.get_disassembly_text()
        ]
        label = _label_escape("\\l".join(lines)) + "\\l"
        nodes.append(f'  {_node_name(block)}[{NODE_ATTRIBUTES} label="{label}"];')

    for block in function.basic_blocks:
        for edge in block.outgoing_edges:
            edges.append(f"  {_node_name(block)} -> {_node_name(edge.target)};")

    return "\n".join(["digraph {"] + edges + [""] + nodes + ["}"])
