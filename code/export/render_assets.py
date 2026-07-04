from __future__ import annotations

import hashlib
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import WINDOWS_CONSOLAS, WINDOWS_SIMFANG, ensure_output_dir, latex_to_readable, read_text


EDGE_RE = re.compile(r"([A-Za-z0-9_]+)(?:\s*--\s*([^>-]+)\s*--)?\s*-->\s*([A-Za-z0-9_]+)")
NODE_RE = re.compile(r'([A-Za-z0-9_]+)\s*(\["([^"]+)"\]|\{"([^"]+)"\})')


def load_font(size: int) -> ImageFont.FreeTypeFont:
    if WINDOWS_SIMFANG.exists():
        return ImageFont.truetype(str(WINDOWS_SIMFANG), size=size)
    return ImageFont.load_default()


def load_formula_font(size: int) -> ImageFont.FreeTypeFont:
    if WINDOWS_CONSOLAS.exists():
        return ImageFont.truetype(str(WINDOWS_CONSOLAS), size=size)
    if WINDOWS_SIMFANG.exists():
        return ImageFont.truetype(str(WINDOWS_SIMFANG), size=size)
    return ImageFont.load_default()


def wrap_node_text(text: str) -> str:
    return text.replace("<br/>", "\n").replace("<br>", "\n")


def wrap_text_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    wrapped_lines: list[str] = []
    for raw_line in wrap_node_text(text).splitlines() or [text]:
        current = ""
        for char in raw_line:
            candidate = current + char
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if current and (bbox[2] - bbox[0]) > max_width:
                wrapped_lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current = candidate
        wrapped_lines.append(current.rstrip() or raw_line)
    return [line for line in wrapped_lines if line] or [text]


def extract_nodes_and_edges(mermaid_text: str) -> tuple[str, dict[str, dict], list[tuple[str, str, str | None]]]:
    lines = [line.rstrip() for line in mermaid_text.splitlines() if line.strip()]
    direction = "TD"
    if lines and lines[0].startswith("flowchart"):
        parts = lines[0].split()
        if len(parts) >= 2:
            direction = parts[1]

    nodes: dict[str, dict] = {}
    edges: list[tuple[str, str, str | None]] = []

    def ensure_node(node_id: str, label: str | None = None, shape: str = "rect") -> None:
        if node_id not in nodes:
            nodes[node_id] = {"label": label or node_id, "shape": shape}
        elif label:
            nodes[node_id]["label"] = label
            nodes[node_id]["shape"] = shape

    for line in lines[1:]:
        for match in NODE_RE.finditer(line):
            node_id = match.group(1)
            label = match.group(3) or match.group(4) or node_id
            shape = "diamond" if match.group(4) else "rect"
            ensure_node(node_id, wrap_node_text(label), shape)

        edge_match = EDGE_RE.search(line)
        if edge_match:
            src = edge_match.group(1)
            edge_label = edge_match.group(2).strip() if edge_match.group(2) else None
            dst = edge_match.group(3)
            ensure_node(src)
            ensure_node(dst)
            edges.append((src, dst, edge_label))

    return direction, nodes, edges


def assign_layers(direction: str, nodes: dict[str, dict], edges: list[tuple[str, str, str | None]]) -> dict[str, tuple[int, int]]:
    incoming = {node_id: 0 for node_id in nodes}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for src, dst, _ in edges:
        incoming[dst] += 1
        outgoing[src].append(dst)

    ready = [node_id for node_id, count in incoming.items() if count == 0]
    if not ready:
        ready = list(nodes.keys())

    layer_map: dict[str, int] = {node_id: 0 for node_id in nodes}
    queue = ready[:]
    seen: set[str] = set()
    while queue:
        node_id = queue.pop(0)
        seen.add(node_id)
        for nxt in outgoing[node_id]:
            layer_map[nxt] = max(layer_map[nxt], layer_map[node_id] + 1)
            incoming[nxt] -= 1
            if incoming[nxt] <= 0 and nxt not in seen:
                queue.append(nxt)

    groups: dict[int, list[str]] = {}
    for node_id, layer in layer_map.items():
        groups.setdefault(layer, []).append(node_id)
    for layer in groups:
        groups[layer].sort()

    positions: dict[str, tuple[int, int]] = {}
    for layer, node_ids in sorted(groups.items()):
        for order, node_id in enumerate(node_ids):
            if direction == "LR":
                positions[node_id] = (layer, order)
            else:
                positions[node_id] = (order, layer)
    return positions


def draw_diamond(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], outline: str, fill: str) -> None:
    x0, y0, x1, y1 = box
    points = [
        ((x0 + x1) // 2, y0),
        (x1, (y0 + y1) // 2),
        ((x0 + x1) // 2, y1),
        (x0, (y0 + y1) // 2),
    ]
    draw.polygon(points, outline=outline, fill=fill)


def render_mermaid_to_png(mermaid_path: Path, output_path: Path) -> Path:
    mermaid_text = read_text(mermaid_path)
    direction, nodes, edges = extract_nodes_and_edges(mermaid_text)
    positions = assign_layers(direction, nodes, edges)

    base_node_w = 300
    base_node_h = 120
    margin = 80

    probe_image = Image.new("RGB", (10, 10), "white")
    probe_draw = ImageDraw.Draw(probe_image)
    font = load_font(20)
    small_font = load_font(16)
    line_spacing = 10
    node_layout: dict[str, dict] = {}
    max_node_w = base_node_w
    max_node_h = base_node_h
    for node_id, node in nodes.items():
        lines = wrap_text_to_width(probe_draw, node["label"], font, max_width=base_node_w - 48)
        widths = []
        heights = []
        for line in lines:
            bbox = probe_draw.textbbox((0, 0), line, font=font)
            widths.append(bbox[2] - bbox[0])
            heights.append(bbox[3] - bbox[1])
        text_w = max(widths or [0])
        text_h = sum(heights or [0]) + line_spacing * max(len(lines) - 1, 0)
        box_w = max(base_node_w, text_w + 48)
        box_h = max(base_node_h, text_h + 40)
        node_layout[node_id] = {"lines": lines, "width": box_w, "height": box_h}
        max_node_w = max(max_node_w, box_w)
        max_node_h = max(max_node_h, box_h)

    step_x = max_node_w + 120
    step_y = max_node_h + 90
    max_x = max(pos[0] for pos in positions.values()) if positions else 0
    max_y = max(pos[1] for pos in positions.values()) if positions else 0
    width = margin * 2 + max_x * step_x + max_node_w
    height = margin * 2 + max_y * step_y + max_node_h

    image = Image.new("RGB", (max(width, 900), max(height, 560)), "white")
    draw = ImageDraw.Draw(image)
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for node_id, (gx, gy) in positions.items():
        node_w = node_layout[node_id]["width"]
        node_h = node_layout[node_id]["height"]
        x0 = margin + gx * step_x
        y0 = margin + gy * step_y
        box = (x0, y0, x0 + node_w, y0 + node_h)
        boxes[node_id] = box

    for src, dst, edge_label in edges:
        sx0, sy0, sx1, sy1 = boxes[src]
        dx0, dy0, dx1, dy1 = boxes[dst]
        start = ((sx0 + sx1) // 2, (sy0 + sy1) // 2)
        end = ((dx0 + dx1) // 2, (dy0 + dy1) // 2)
        if direction == "LR":
            start = (sx1, (sy0 + sy1) // 2)
            end = (dx0, (dy0 + dy1) // 2)
        elif direction == "TD":
            start = ((sx0 + sx1) // 2, sy1)
            end = ((dx0 + dx1) // 2, dy0)

        draw.line([start, end], fill="#4f6fa3", width=4)
        arrow = 10
        if direction == "LR":
            draw.polygon([end, (end[0] - arrow, end[1] - arrow), (end[0] - arrow, end[1] + arrow)], fill="#4f6fa3")
        else:
            draw.polygon([end, (end[0] - arrow, end[1] - arrow), (end[0] + arrow, end[1] - arrow)], fill="#4f6fa3")
        if edge_label:
            label_text = wrap_node_text(edge_label)
            lx = (start[0] + end[0]) // 2
            ly = (start[1] + end[1]) // 2 - 20
            draw.text((lx, ly), label_text, fill="#2a2a2a", font=small_font, anchor="mm")

    for node_id, node in nodes.items():
        box = boxes[node_id]
        fill = "#eef3fb"
        outline = "#355d96"
        if node["shape"] == "diamond":
            draw_diamond(draw, box, outline=outline, fill=fill)
        else:
            draw.rounded_rectangle(box, radius=18, outline=outline, fill=fill, width=4)

        text = "\n".join(node_layout[node_id]["lines"])
        center = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        draw.multiline_text(center, text, font=font, fill="#1b1b1b", anchor="mm", align="center", spacing=line_spacing)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def _normalize_matrix_block(text: str) -> str:
    matrix_match = re.search(
        r"(?P<prefix>.*?)\\begin\{bmatrix\}(?P<body>.*?)\\end\{bmatrix\}(?P<suffix>.*)",
        text,
        flags=re.DOTALL,
    )
    if not matrix_match:
        return text

    prefix = latex_to_readable(matrix_match.group("prefix")).strip()
    suffix = latex_to_readable(matrix_match.group("suffix")).strip()
    body = matrix_match.group("body")
    rows = []
    for raw_row in body.split(r"\\"):
        cells = [latex_to_readable(cell).strip() for cell in raw_row.split("&")]
        if any(cells):
            rows.append(cells)

    widths = []
    for col in range(max(len(row) for row in rows)):
        widths.append(max(len(row[col]) if col < len(row) else 0 for row in rows))

    matrix_lines = []
    for idx, row in enumerate(rows):
        padded = []
        for col, width in enumerate(widths):
            cell = row[col] if col < len(row) else ""
            padded.append(cell.ljust(width))
        joined = "  ".join(padded).rstrip()
        if idx == 0:
            matrix_lines.append(f"{prefix} [ {joined}")
        elif idx == len(rows) - 1:
            matrix_lines.append(f"{' ' * len(prefix)}   {joined} ] {suffix}".rstrip())
        else:
            matrix_lines.append(f"{' ' * len(prefix)}   {joined}")
    return "\n".join(matrix_lines)


def render_formula_to_lines(formula_block: str) -> list[str]:
    text = _normalize_matrix_block(formula_block.strip())
    lines = [latex_to_readable(line) for line in text.splitlines() if line.strip()]
    return lines or [latex_to_readable(formula_block)]


def render_formula_to_png(formula_block: str, output_path: Path) -> Path:
    lines = render_formula_to_lines(formula_block)
    font = load_formula_font(26)
    padding_x = 36
    padding_y = 28
    line_gap = 14

    dummy = Image.new("RGB", (10, 10), "white")
    draw = ImageDraw.Draw(dummy)
    widths = []
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])

    width = max(widths or [200]) + padding_x * 2
    height = sum(heights or [30]) + line_gap * max(len(lines) - 1, 0) + padding_y * 2
    image = Image.new("RGB", (max(width, 300), max(height, 90)), "white")
    draw = ImageDraw.Draw(image)

    y = padding_y
    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        draw.text(((image.width - line_width) / 2, y), line, fill="#222222", font=font)
        y += (bbox[3] - bbox[1]) + line_gap

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def stable_render_path(rendered_assets_dir: Path, kind: str, source_key: str, suffix: str) -> Path:
    digest = hashlib.md5(source_key.encode("utf-8")).hexdigest()[:12]
    path = rendered_assets_dir / kind / f"{digest}.{suffix}"
    ensure_output_dir(path.parent)
    return path
