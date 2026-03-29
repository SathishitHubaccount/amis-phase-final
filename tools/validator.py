"""
AMIS Scenario Validator
========================
Compares what an agent actually said against what it SHOULD have said,
given a controlled set of injected test data.

Usage:
    from tools.validator import ScenarioValidator
    from tools.scenario import CRISIS_SCENARIO

    validator = ScenarioValidator(CRISIS_SCENARIO, agent_final_answer)
    results   = validator.validate()
    print(validator.render_report(results))
"""
from datetime import datetime

W = 78  # display width


class ScenarioValidator:
    """
    Validates an agent's final answer against a scenario's expected_checks.

    Each check specifies:
      - search_terms : list of strings to look for in the agent's answer
      - match_mode   : "any"  → PASS if at least one term is found
                       "all"  → PASS if every term is found
                       "none" → PASS if NO term is found (used for negative checks)
      - required     : True → counts toward required pass/fail verdict
    """

    def __init__(self, scenario: dict, final_answer: str):
        self.scenario = scenario
        self.answer   = final_answer
        self.answer_lower = final_answer.lower()

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def validate(self) -> list[dict]:
        """
        Run all checks in scenario["expected_checks"].

        Returns:
            List of result dicts, one per check:
            {
                "id":          str,
                "category":    str,
                "description": str,
                "required":    bool,
                "passed":      bool,
                "match_mode":  str,
                "matched_term": str | None,   # the term that triggered the match
            }
        """
        results = []
        for check in self.scenario.get("expected_checks", []):
            passed, matched_term = self._run_check(check)
            results.append({
                "id":           check["id"],
                "category":     check.get("category", ""),
                "description":  check["description"],
                "required":     check.get("required", True),
                "passed":       passed,
                "match_mode":   check.get("match_mode", "any"),
                "matched_term": matched_term,
                "search_terms": check.get("search_terms", []),
            })
        return results

    def render_report(self, results: list[dict]) -> str:
        """
        Render a human-readable validation report.

        Returns:
            Formatted multi-line string.
        """
        lines = []

        def divider(char="─"):
            lines.append(char * W)

        # ── Header ──
        lines.append("╔" + "═" * (W - 2) + "╗")
        header = "  SCENARIO VALIDATION REPORT"
        lines.append("║" + header + " " * (W - 2 - len(header)) + "║")
        lines.append("╚" + "═" * (W - 2) + "╝")
        lines.append(f"  Scenario   : {self.scenario['name']}")
        lines.append(f"  Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # ── Injected data summary ──
        lines.append("")
        divider()
        lines.append("  INJECTED TEST DATA")
        lines.append("  (These exact values were fed to the agent — NOT the normal simulated data)")
        divider()
        for item in self.scenario.get("injected_values_summary", []):
            lines.append(f"  ✦ {item}")

        # ── Checks ──
        required_checks = [r for r in results if r["required"]]
        optional_checks = [r for r in results if not r["required"]]

        required_passed = sum(1 for r in required_checks if r["passed"])
        optional_passed = sum(1 for r in optional_checks if r["passed"])
        total_passed    = sum(1 for r in results if r["passed"])

        lines.append("")
        divider()
        lines.append(f"  REQUIRED CHECKS  ({required_passed}/{len(required_checks)} passed)")
        lines.append("  These are the signals the agent MUST identify from the injected data.")
        divider()
        for r in required_checks:
            lines.extend(self._format_check(r))

        if optional_checks:
            lines.append("")
            divider()
            lines.append(f"  OPTIONAL CHECKS  ({optional_passed}/{len(optional_checks)} passed)")
            lines.append("  Nice-to-have signals — failure does not affect the overall verdict.")
            divider()
            for r in optional_checks:
                lines.extend(self._format_check(r))

        # ── Score and Verdict ──
        lines.append("")
        divider("═")
        lines.append("  SCORE & VERDICT")
        divider("═")

        score_line = (
            f"  Required  : {required_passed}/{len(required_checks)} passed"
            f"  |  Optional: {optional_passed}/{len(optional_checks)} passed"
            f"  |  Total: {total_passed}/{len(results)}"
        )
        lines.append(score_line)
        lines.append("")

        all_required_passed = required_passed == len(required_checks)

        if all_required_passed and optional_passed == len(optional_checks):
            verdict = "PASS — PERFECT"
            detail  = "Agent correctly identified ALL injected signals (required + optional)."
            proof   = "The agent IS reasoning over real tool data and producing correct conclusions."
        elif all_required_passed:
            verdict = "PASS"
            detail  = f"Agent correctly identified all {len(required_checks)} required signals."
            missed  = [r["description"] for r in optional_checks if not r["passed"]]
            proof   = f"Missed optional: {missed[0]}" if missed else ""
            proof  += "\nThe agent IS reasoning over real tool data and producing correct conclusions."
        elif required_passed >= len(required_checks) // 2:
            verdict = "PARTIAL PASS"
            missed  = [r["description"] for r in required_checks if not r["passed"]]
            detail  = f"Agent missed {len(required_checks) - required_passed} required signal(s)."
            proof   = f"Missed: {'; '.join(missed[:2])}"
        else:
            verdict = "FAIL"
            missed  = [r["description"] for r in required_checks if not r["passed"]]
            detail  = f"Agent failed {len(required_checks) - required_passed} required checks."
            proof   = f"Missed: {'; '.join(missed[:3])}"

        lines.append(f"  VERDICT  : {verdict}")
        lines.append(f"  DETAIL   : {detail}")
        if proof:
            lines.append(f"  NOTE     : {proof.strip()}")

        divider("═")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _run_check(self, check: dict) -> tuple[bool, str | None]:
        """
        Run a single check.
        Returns (passed: bool, matched_term: str | None).
        """
        terms      = check.get("search_terms", [])
        match_mode = check.get("match_mode", "any")
        answer     = self.answer_lower

        if match_mode == "none":
            # PASS if NONE of the terms appear
            for term in terms:
                if term.lower() in answer:
                    return False, term   # found something it shouldn't say
            return True, None

        if match_mode == "all":
            for term in terms:
                if term.lower() not in answer:
                    return False, None
            return True, terms[0] if terms else None

        # Default: "any"
        for term in terms:
            if term.lower() in answer:
                return True, term
        return False, None

    def _format_check(self, result: dict) -> list[str]:
        """Format a single check result as lines."""
        lines = []
        icon = "✓ PASS" if result["passed"] else "✗ FAIL"
        marker = "[PASS]" if result["passed"] else "[FAIL]"

        lines.append("")
        lines.append(f"  {marker}  {result['category']}")
        lines.append(f"         {result['description']}")

        if result["passed"] and result["matched_term"]:
            mode = result["match_mode"]
            if mode == "none":
                lines.append(f"         Result  : No forbidden terms found — correct.")
            else:
                lines.append(f"         Matched : \"{result['matched_term']}\" found in agent response")
        elif not result["passed"]:
            mode = result["match_mode"]
            if mode == "none":
                lines.append(f"         Found   : \"{result['matched_term']}\" — agent should NOT say this for healthy state")
            else:
                terms_preview = result.get("search_terms", [])[:4]
                lines.append(f"         Searched: {terms_preview} — none found in response")

        return lines
