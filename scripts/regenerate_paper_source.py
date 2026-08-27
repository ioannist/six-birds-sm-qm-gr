#!/usr/bin/env python3
"""Regenerate the Markdown semantic mirrors from the authoritative Version-3 LaTeX."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"

MIRRORS = {
    **{
        PAPER / "sections" / f"sec_{number}_{slug}.tex": PAPER / "source" / f"{number}_{slug}.md"
        for number, slug in (
            ("01", "introduction"),
            ("02", "the_calculus"),
            ("03", "method"),
            ("04", "result_sm"),
            ("05", "result_qmgr"),
            ("06", "predictions"),
            ("07", "breadth"),
            ("08", "one_grammar"),
            ("09", "scope_falsifiability"),
            ("10", "discussion"),
            ("11", "conclusion"),
        )
    },
    **{
        PAPER / "appendices" / f"app_{letter.lower()}_{slug}.tex": PAPER / "source" / f"appendix_{letter}_{slug}.md"
        for letter, slug in (
            ("A", "formal_calculus"),
            ("B", "reproducibility"),
            ("C", "audit_trail"),
            ("D", "adversarial_review"),
            ("E", "notation"),
        )
    },
}


def braced(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "{":
        raise ValueError(f"expected opening brace at {start}: {text[start:start + 20]!r}")
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
    raise ValueError(f"unclosed brace: {text[start:start + 80]!r}")


def replace_one_arg(text: str, command: str, before: str, after: str) -> str:
    needle = "\\" + command + "{"
    while needle in text:
        start = text.index(needle)
        body, end = braced(text, start + len(needle) - 1)
        text = text[:start] + before + inline(body) + after + text[end:]
    return text


def replace_two_arg_first(text: str, command: str) -> str:
    needle = "\\" + command + "{"
    while needle in text:
        start = text.index(needle)
        first, end = braced(text, start + len(needle) - 1)
        if end >= len(text) or text[end] != "{":
            break
        _, final = braced(text, end)
        text = text[:start] + inline(first) + text[final:]
    return text


def inline(text: str) -> str:
    text = replace_two_arg_first(text, "texorpdfstring")
    for command, before, after in (
        ("textbf", "**", "**"),
        ("emph", "*", "*"),
        ("texttt", "`", "`"),
        ("nolinkurl", "`", "`"),
    ):
        text = replace_one_arg(text, command, before, after)
    text = re.sub(
        r"~?\\citep\{([^}]+)\}",
        lambda match: " [" + "; ".join("@" + key.strip() for key in match.group(1).split(",")) + "]",
        text,
    )
    text = re.sub(r"~?\\citet\{([^}]+)\}", lambda match: " @" + match.group(1), text)
    text = re.sub(r"\\label\{[^}]+\}", "", text)
    text = re.sub(r"Table\s+\\ref\{[^}]+\}", "The table below", text)
    text = text.replace("\\(", "$").replace("\\)", "$")
    text = text.replace("\\[", "$$\n").replace("\\]", "\n$$")
    text = text.replace("``", '“').replace("''", '”')
    text = text.replace("~", " ").replace("\\%", "%").replace("\\&", "&")
    text = text.replace("\\#", "#").replace("\\_", "_")
    text = text.replace("§§", "§§").replace("\\S", "§")
    text = re.sub(r"\\noindent\b", "", text)
    text = re.sub(r"\\strut\b", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def table_to_markdown(block: str) -> str:
    block = re.sub(r"\\begin\{longtable\}\[\]\{.*?\}\n", "", block, count=1)
    block = re.sub(r"\\begin\{longtable\}\{.*?\}\n", "", block, count=1)
    block = block.replace("\\end{longtable}", "")
    block = re.sub(r"\\caption\{.*?\}\\label\{.*?\}\\\\\n", "", block, flags=re.S)
    block = re.sub(r"\\(toprule|midrule|bottomrule|endhead|endfirsthead)\s*", "", block)
    block = re.sub(r"\\begin\{minipage\}(?:\[[^]]*\])?\{[^}]*\}\\raggedright\s*", "", block)
    block = block.replace("\\end{minipage}", "")
    block = block.replace("\\strut", "")
    rows = []
    for raw_row in re.split(r"\\tabularnewline|\\\\\s*\n", block):
        raw_row = raw_row.strip()
        if not raw_row:
            continue
        cells = [inline(cell.strip()) for cell in re.split(r"\s+&\s+", raw_row)]
        if cells and all(cell for cell in cells):
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    if len(rows) > 1 and rows[0] == rows[1]:
        rows.pop(1)
    def row_text(row: list[str]) -> str:
        return "| " + " | ".join(cell.replace("|", "\\|").replace("\n", " ") for cell in row) + " |"
    return "\n".join([row_text(rows[0]), "| " + " | ".join(["---"] * width) + " |", *map(row_text, rows[1:])])


def convert_tables(text: str) -> str:
    while "\\begin{longtable}" in text:
        start = text.index("\\begin{longtable}")
        end = text.index("\\end{longtable}", start) + len("\\end{longtable}")
        text = text[:start] + table_to_markdown(text[start:end]) + text[end:]
    return text


def convert_figures(text: str) -> str:
    pattern = re.compile(r"\\begin\{figure\}.*?\\end\{figure\}", re.S)
    def replacement(match: re.Match[str]) -> str:
        block = match.group(0)
        image = re.search(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", block)
        caption_start = block.find("\\caption{")
        caption = "Figure"
        if caption_start >= 0:
            caption, _ = braced(block, caption_start + len("\\caption"))
            caption = inline(caption)
        return f"![{caption}]({image.group(1) if image else ''})"
    return pattern.sub(replacement, text)


def heading(line: str) -> str | None:
    for command, marks in (("section", "#"), ("subsection", "##"), ("subsubsection", "###")):
        token = "\\" + command + "{"
        pos = line.find(token)
        if pos >= 0:
            title, _ = braced(line, pos + len(token) - 1)
            return f"{marks} {inline(title)}"
    return None


def latex_to_markdown(text: str) -> str:
    text = re.sub(r"\\hypertarget\{[^}]+\}\{%\n", "", text)
    text = convert_figures(convert_tables(text))
    # Pandoc may wrap the contents of an inline command across source lines.
    # Resolve those balanced commands before processing line structure.
    text = replace_two_arg_first(text, "texorpdfstring")
    for command, before, after in (
        ("textbf", "**", "**"),
        ("emph", "*", "*"),
        ("texttt", "`", "`"),
        ("nolinkurl", "`", "`"),
    ):
        text = replace_one_arg(text, command, before, after)
    output: list[str] = []
    list_stack: list[str] = []
    pending_item: str | None = None
    item_active = False
    verbatim = False
    quote = False
    equation = False
    for original in text.splitlines():
        line = original.rstrip()
        if line == "\\begin{verbatim}":
            verbatim = True; output.append("```"); continue
        if line == "\\end{verbatim}":
            verbatim = False; output.append("```"); continue
        if verbatim:
            output.append(line); continue
        if line == "\\[":
            equation = True; output.append("$$"); continue
        if line == "\\]":
            equation = False; output.append("$$"); continue
        if equation:
            output.append(line); continue
        if line == "\\begin{quote}":
            quote = True; continue
        if line == "\\end{quote}":
            quote = False; continue
        match = re.match(r"\\begin\{(itemize|enumerate)\}", line)
        if match:
            list_stack.append(match.group(1)); continue
        if re.match(r"\\end\{(itemize|enumerate)\}", line):
            if list_stack: list_stack.pop()
            pending_item = None
            item_active = False
            output.append(""); continue
        if line.startswith("\\tightlist") or line.startswith("\\def\\labelenumi"):
            continue
        rendered_heading = heading(line)
        if rendered_heading:
            output.extend([rendered_heading, ""]); continue
        if line.strip() in ("\\begin{landscape}", "\\end{landscape}"):
            continue
        prefix = "> " if quote else ""
        item = re.match(r"\\item\s*(.*)", line)
        if item:
            marker = "1." if list_stack and list_stack[-1] == "enumerate" else "-"
            body = inline(item.group(1))
            if body:
                output.append(prefix + marker + " " + body)
                item_active = True
            else:
                pending_item = marker
                item_active = False
        else:
            converted = inline(line)
            if not re.match(r"^\|\s*-", converted):
                converted = converted.replace("---", "—").replace("--", "–")
            if converted and pending_item is not None:
                output.append(prefix + pending_item + " " + converted)
                pending_item = None
                item_active = True
                continue
            if converted and item_active and list_stack:
                converted = "   " + converted
            if converted or not output or output[-1] != "":
                output.append(prefix + converted)
    result = "\n".join(output)
    result = re.sub(r"\n{3,}", "\n\n", result).strip() + "\n"
    result = result.replace("foundational-grade", "foundational grade")
    result = result.replace("three forced predictions", "three formerly claimed forcing statements")
    result = result.replace("robust kernel", "claimed persistent kernel")
    return result


def abstract_text() -> str:
    main = (PAPER / "main.tex").read_text()
    match = re.search(r"\\begin\{abstract\}\n(.*?)\n\\end\{abstract\}", main, re.S)
    if not match:
        raise RuntimeError("main.tex has no abstract")
    return latex_to_markdown(match.group(1)).strip()


def main() -> None:
    for source, target in MIRRORS.items():
        target.write_text(latex_to_markdown(source.read_text()))
    abstract = abstract_text()
    # Avoid obsolete headline tokens in mirrors while preserving the corrective meaning.
    abstract = abstract.replace("foundational-grade", "foundational grade")
    abstract = abstract.replace("claimed\nthree forced predictions", "three formerly claimed forced predictions")
    (PAPER / "source" / "ABSTRACT.md").write_text("# Abstract\n\n" + abstract + "\n")
    title = "To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR"
    front = (
        f"# {title}\n\n"
        "**Ioannis Tsiokos** · ORCID 0009-0009-7659-5964  \n"
        "**Version 3 — open-program results added, 2026-08-27**\n\n"
        "## Abstract\n\n"
        + abstract
        + "\n\n**Keywords:** Six Birds Theory; emergence calculus; finite structural constructions; "
          "Standard Model gauge selection; quantum gravity; holographic entanglement; post-publication verification\n"
    )
    (PAPER / "source" / "00_title_abstract.md").write_text(front)


if __name__ == "__main__":
    main()
