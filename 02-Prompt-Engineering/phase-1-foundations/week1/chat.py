"""Week 1 PRACTICAL — a reusable AI assistant in your terminal.

Run:  python -m week1.chat
      python -m week1.chat --model gpt-5-nano --system "You are a SQL tutor."

All the real logic lives in ai_core/assistant.py; this file is only the UI.
Keeping UI and logic separate is what makes the Assistant reusable in
Week 2 (prompt library) and Week 3 (lesson generator) without changes.

Commands:  /reset  /usage  /history  /system <text>  /model <name>  /quit
"""
import argparse

from ai_core import Assistant, AssistantError, MissingAPIKeyError

HELP = "Commands: /reset  /usage  /history  /system <text>  /model <name>  /quit"


def main() -> None:
    p = argparse.ArgumentParser(description="Terminal AI assistant")
    p.add_argument("--model")
    p.add_argument("--system", default="You are a helpful, concise assistant.")
    p.add_argument("--max-output-tokens", type=int)
    p.add_argument("--log", default="logs/chat.jsonl", help="JSONL log of every call")
    args = p.parse_args()

    try:
        bot = Assistant(instructions=args.system, model=args.model,
                        max_output_tokens=args.max_output_tokens, log_path=args.log)
    except MissingAPIKeyError as e:
        raise SystemExit(str(e))

    print(f"Model: {bot.model}\n{HELP}\n")
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.startswith("/"):
            cmd, _, arg = line.partition(" ")
            if cmd == "/quit":
                break
            elif cmd == "/reset":
                bot.reset()
                print("(history cleared)")
            elif cmd == "/usage":
                print(bot.usage)
            elif cmd == "/history":
                for m in bot.history:
                    print(f"  {m['role']}: {m['content'][:80]}")
            elif cmd == "/system" and arg:
                bot.instructions = arg
                print("(system instructions updated)")
            elif cmd == "/model" and arg:
                bot.model = arg
                print(f"(model -> {arg})")
            else:
                print(HELP)
            continue

        try:
            reply = bot.ask(line)
        except AssistantError as e:
            print(f"!! {e}")
            continue
        print(f"\nai> {reply.text}\n")
        if reply.status != "completed":
            print(f"!! answer is INCOMPLETE ({reply.incomplete_reason}) — raise --max-output-tokens")
        print(f"    {reply.stats()}\n")

    print(f"\nSession usage: {bot.usage}")


if __name__ == "__main__":
    main()
