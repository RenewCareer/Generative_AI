"""Run every template's tests against a real model and report pass rates.

    python -m week2.prompt_library.run_tests                       # all templates
    python -m week2.prompt_library.run_tests -t classify_ticket    # one template
    python -m week2.prompt_library.run_tests --repeat 3            # expose flakiness
    python -m week2.prompt_library.run_tests --model gpt-5-nano    # compare models
    python -m week2.prompt_library.run_tests --validate-only       # no API calls

Results are saved to results/<timestamp>.json tagged with template@version and
model, so you can compare runs before and after editing a prompt.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ai_core import Assistant, AssistantError

from .checks import run_check
from .library import PromptTemplate, load_library


def run_template(bot: Assistant, t: PromptTemplate, repeat: int, verbose: bool) -> dict:
    cases = []
    for test in t.tests:
        for i in range(repeat):
            prompt = t.render(**test.vars)
            try:
                reply = bot.complete(prompt, instructions=t.instructions)
                output, status = reply.text, reply.status
            except AssistantError as e:
                output, status = f"<ERROR> {e}", "error"
            results = [(spec, *run_check(output, spec)) for spec in test.checks]
            passed = status == "completed" and all(ok for _, ok, _ in results)
            cases.append({
                "test": test.name, "run": i, "passed": passed, "status": status,
                "output": output,
                "checks": [{"type": s["type"], "ok": ok, "detail": d} for s, ok, d in results],
            })
            if verbose or not passed:
                mark = "PASS" if passed else "FAIL"
                print(f"   [{mark}] {test.name} #{i}")
                for s, ok, d in results:
                    if verbose or not ok:
                        print(f"        {'✓' if ok else '✗'} {s['type']}: {d}")
                if not passed:
                    print("        output: " + output[:300].replace("\n", "\n                "))
    n_pass = sum(c["passed"] for c in cases)
    return {"template": t.id, "passed": n_pass, "total": len(cases), "cases": cases}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("-t", "--template", action="append", help="template name (repeatable)")
    p.add_argument("--model")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--validate-only", action="store_true")
    args = p.parse_args()

    lib = load_library()
    selected = [lib[n] for n in args.template] if args.template else list(lib.values())

    problems = {t.id: t.validate() for t in selected}
    problems = {k: v for k, v in problems.items() if v}
    if problems:
        for tid, issues in problems.items():
            print(f"✗ {tid}: " + "; ".join(issues))
        raise SystemExit("Fix static template problems before spending tokens.")
    print(f"✓ {len(selected)} templates pass static validation")
    if args.validate_only:
        return

    bot = Assistant(model=args.model, remember_history=False)
    summary = []
    for t in selected:
        print(f"\n▶ {t.id}  ({t.category})")
        summary.append(run_template(bot, t, args.repeat, args.verbose))

    print("\n" + "=" * 60)
    print(f"{'template':<40}{'pass rate':>12}")
    for s in summary:
        rate = s["passed"] / s["total"]
        flag = "" if rate == 1 else "  <-- investigate"
        print(f"{s['template']:<40}{s['passed']:>5}/{s['total']:<3} {rate:>4.0%}{flag}")
    total_pass = sum(s["passed"] for s in summary)
    total = sum(s["total"] for s in summary)
    print(f"\nOVERALL {total_pass}/{total} ({total_pass / total:.0%}) on {bot.model} | {bot.usage}")

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"prompt_library_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps({"model": bot.model, "repeat": args.repeat,
                                "usage": str(bot.usage), "templates": summary},
                               indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {path}")


if __name__ == "__main__":
    main()
