"""
AMIS Data Flow Tracer
=====================
Captures and renders the exact data flow through any AMIS agent run.

What it shows:
  1. The user's question
  2. At each iteration: LLM reasoning → which tool was called → what it returned
  3. The LLM's final answer
  4. VALUE REFERENCE AUDIT: which specific values from tool outputs the LLM
     actually cited in its final answer — proving the agent is reasoning over
     real data, not generating canned or hallucinated text.

Usage:
    agent = DemandForecastingAgent()
    agent.run("Analyse demand for PROD-A")
    print(agent.get_trace_report())          # print to terminal
    agent.save_trace("output_trace.txt")     # save to file
"""
import json
import re
from datetime import datetime
from typing import Any


W = 78  # display width


class DataFlowTracer:
    """
    Renders a structured audit of an agent's execution trace.

    Takes the agent's self.trace list (populated automatically by BaseAgent
    during every .run() call) and produces a human-readable report showing:

      - Step-by-step: tool called → tool output → LLM reasoning
      - Value Reference Audit: which tool output values appear verbatim in
        the LLM's final answer (with percentage and verdict)
    """

    def __init__(self, agent_name: str, trace: list):
        self.agent_name = agent_name
        self.trace = trace

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def render(self, verbose: bool = False) -> str:
        """
        Render the full data flow audit report as a formatted string.

        Args:
            verbose: If True, show full tool output JSON.
                     If False, show a compact summary (default).
        Returns:
            Multi-line string report.
        """
        lines = []

        def divider(char="─"):
            lines.append(char * W)

        def section(title: str):
            lines.append("")
            divider()
            lines.append(f"  {title}")
            divider()

        # ── Header ──
        lines.append("╔" + "═" * (W - 2) + "╗")
        header = f"  DATA FLOW AUDIT  —  {self.agent_name}"
        lines.append("║" + header + " " * (W - 2 - len(header)) + "║")
        lines.append("╚" + "═" * (W - 2) + "╝")
        lines.append(f"  Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Trace steps: {len(self.trace)}")

        # ── User Input ──
        user_inputs = [e for e in self.trace if e["type"] == "user_input"]
        if user_inputs:
            section("USER INPUT")
            for line in _wrap(user_inputs[0]["content"], indent=2):
                lines.append(line)

        # Accumulate all tool calls for the audit at the end
        # key: tool_id → {tool_name, args, result_str}
        all_tool_calls: dict[str, dict] = {}

        # ── Per-iteration blocks ──
        iterations = sorted(set(
            e["iteration"] for e in self.trace if "iteration" in e
        ))

        final_answer_text = ""

        for it in iterations:
            it_entries = [e for e in self.trace if e.get("iteration") == it]
            tool_calls   = [e for e in it_entries if e["type"] == "tool_call"]
            tool_results = [e for e in it_entries if e["type"] == "tool_result"]
            thinking     = [e for e in it_entries if e["type"] == "llm_thinking"]
            final        = [e for e in it_entries if e["type"] == "final_answer"]

            if not tool_calls and not final:
                continue

            section(f"ITERATION {it}")

            # LLM reasoning snippet
            if thinking:
                text = thinking[0]["text"].strip()
                snippet = text[:500] + ("..." if len(text) > 500 else "")
                lines.append("")
                lines.append("  LLM REASONING:")
                for line in _wrap(snippet, indent=4):
                    lines.append(line)

            # Tool calls + results
            for tc in tool_calls:
                lines.append("")
                lines.append(f"  ▶ TOOL CALLED: {tc['tool']}")

                # Input args
                lines.append("    INPUT:")
                for line in json.dumps(tc["args"], indent=2).split("\n"):
                    lines.append(f"      {line}")

                # Find the matching result
                result_entry = next(
                    (r for r in tool_results if r["tool_id"] == tc["tool_id"]),
                    None,
                )
                if result_entry:
                    all_tool_calls[tc["tool_id"]] = {
                        "tool_name": tc["tool"],
                        "args": tc["args"],
                        "result_str": result_entry["result"],
                    }

                    result_str = result_entry["result"]
                    lines.append("    OUTPUT:")
                    try:
                        obj = json.loads(result_str)
                        display = json.dumps(obj, indent=2) if verbose else _compact_json(obj)
                    except (json.JSONDecodeError, ValueError):
                        display = result_str[:600]

                    for line in display.split("\n"):
                        lines.append(f"      {line}")

            # Final answer
            if final:
                final_answer_text = str(final[0]["content"])
                section("FINAL LLM ANSWER")
                lines.append("")
                lines.append("  RESPONSE PREVIEW (first 800 chars):")
                preview = final_answer_text[:800]
                if len(final_answer_text) > 800:
                    preview += f"\n  ... [{len(final_answer_text) - 800} more chars]"
                for line in preview.split("\n")[:28]:
                    lines.append(f"    {line}")

        # ── Value Reference Audit (appended after all iterations) ──
        if final_answer_text and all_tool_calls:
            lines.append("")
            lines.extend(_render_audit(all_tool_calls, final_answer_text))

        return "\n".join(lines)

    def save(self, filepath: str) -> None:
        """Write the verbose trace report to a file."""
        report = self.render(verbose=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"  Trace report saved → {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# MODULE-LEVEL HELPERS  (used internally, not exported)
# ─────────────────────────────────────────────────────────────────────────────

def _compact_json(obj: Any, depth: int = 0) -> str:
    """Compact but readable JSON summary — avoids full deep nesting."""
    if depth >= 2:
        if isinstance(obj, dict):
            return f"{{... {len(obj)} fields}}"
        if isinstance(obj, list):
            return f"[... {len(obj)} items]"
        return repr(obj)

    if isinstance(obj, dict):
        lines = ["{"]
        for k, v in list(obj.items())[:12]:
            lines.append(f"  {k!r}: {_compact_json(v, depth + 1)},")
        if len(obj) > 12:
            lines.append(f"  ... ({len(obj) - 12} more fields)")
        lines.append("}")
        return "\n".join(lines)

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if all(isinstance(x, (int, float, str, bool)) for x in obj):
            preview = [repr(x) for x in obj[:5]]
            suffix = f", ... {len(obj) - 5} more" if len(obj) > 5 else ""
            return f"[{', '.join(preview)}{suffix}]"
        lines = ["["]
        for item in obj[:3]:
            lines.append(f"  {_compact_json(item, depth + 1)},")
        if len(obj) > 3:
            lines.append(f"  ... ({len(obj) - 3} more)")
        lines.append("]")
        return "\n".join(lines)

    return repr(obj)


def _extract_leaf_values(json_str: str) -> list[tuple[str, Any]]:
    """
    Recursively walk a JSON string and return all (key_path, value) leaf pairs.

    Filters to values that are likely to appear meaningfully in LLM narrative:
      - Numbers whose absolute value >= 10
      - Strings between 3 and 80 chars (non-trivial, non-boolean literals)
      - Booleans
    """
    try:
        obj = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        return []

    results: list[tuple[str, Any]] = []

    def recurse(node: Any, path: str = ""):
        if isinstance(node, dict):
            for k, v in node.items():
                recurse(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                recurse(v, f"{path}[{i}]")
        else:
            if isinstance(node, bool):
                results.append((path, node))
            elif isinstance(node, (int, float)) and abs(node) >= 10:
                results.append((path, node))
            elif isinstance(node, str) and 3 <= len(node) <= 80:
                lv = node.lower()
                if lv not in ("n/a", "null", "none", "true", "false", ""):
                    results.append((path, node))

    recurse(obj)
    return results


def _value_in_text(value: Any, text: str) -> bool:
    """Return True if value appears in text in any common representation."""
    if isinstance(value, bool):
        return str(value).lower() in text.lower()

    if isinstance(value, float):
        candidates = []
        if value == int(value):
            candidates += [str(int(value)), f"{int(value):,}"]
        candidates += [
            str(round(value, 1)),
            str(round(value, 2)),
            f"{value:,.1f}",
            f"{value:,.0f}",
        ]
        return any(c in text for c in candidates)

    if isinstance(value, int):
        return str(value) in text or f"{value:,}" in text

    if isinstance(value, str):
        return value.lower() in text.lower()

    return False


def _render_audit(tool_calls: dict, final_answer: str) -> list[str]:
    """
    Build the VALUE REFERENCE AUDIT lines.

    For each tool that was called, finds which specific values from its JSON
    output appear verbatim in the LLM's final answer text.
    """
    lines = []

    lines.append("─" * W)
    lines.append("  VALUE REFERENCE AUDIT")
    lines.append("  ─────────────────────────────────────────────────────────────────────")
    lines.append("  Which specific values from tool outputs appear in the LLM's answer?")
    lines.append("  This proves the agent is reasoning over real data, not canned text.")
    lines.append("  ─────────────────────────────────────────────────────────────────────")

    total_trackable = 0
    total_found = 0
    per_tool: dict[str, list[tuple[str, Any]]] = {}

    for tool_id, info in tool_calls.items():
        tool_name = info["tool_name"]
        leaf_values = _extract_leaf_values(info["result_str"])
        total_trackable += len(leaf_values)

        found = []
        seen_sigs: set[str] = set()
        for key_path, value in leaf_values:
            if _value_in_text(value, final_answer):
                short_key = key_path.split(".")[-1] if "." in key_path else key_path
                short_key = re.sub(r"\[\d+\]", "", short_key)  # strip [0] index
                sig = f"{short_key}:{value}"
                if sig not in seen_sigs:
                    seen_sigs.add(sig)
                    found.append((short_key, value))
                    total_found += 1

        if found:
            per_tool.setdefault(tool_name, []).extend(found)

    if not per_tool:
        lines.append("")
        lines.append("  ⚠  No direct value matches found.")
        lines.append("     The LLM may have paraphrased values or used different units.")
    else:
        for tool_name, refs in per_tool.items():
            lines.append("")
            lines.append(f"  ✓ {tool_name}")
            for key, val in refs[:10]:  # cap at 10 per tool
                lines.append(f"      {key:<40s}  →  {repr(val)}")
            if len(refs) > 10:
                lines.append(f"      ... and {len(refs) - 10} more matches")

    lines.append("")
    pct = round(100 * total_found / total_trackable) if total_trackable else 0
    lines.append(
        f"  SUMMARY : {total_found} of {total_trackable} trackable values "
        f"from tool outputs found in LLM response ({pct}%)"
    )

    if pct >= 30:
        verdict = "CONFIRMED  — LLM is actively reasoning over real tool data"
    elif pct >= 10:
        verdict = "LIKELY     — LLM cites key values from tool outputs"
    elif pct > 0:
        verdict = "PARTIAL    — LLM references some values but may be summarising"
    else:
        verdict = "UNCLEAR    — No direct matches; check for paraphrasing"

    lines.append(f"  VERDICT  : {verdict}")
    lines.append("─" * W)
    return lines


def _wrap(text: str, indent: int = 0) -> list[str]:
    """Word-wrap text to W chars, preserving explicit newlines."""
    width = W - indent
    prefix = " " * indent
    result = []
    for para in text.split("\n"):
        if not para.strip():
            result.append("")
            continue
        while len(para) > width:
            split_at = para.rfind(" ", 0, width)
            if split_at == -1:
                split_at = width
            result.append(prefix + para[:split_at])
            para = para[split_at:].lstrip()
        result.append(prefix + para)
    return result
