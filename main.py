"""Hangover Journal — an AI memory agent powered by Cognee.

Your AI wakes up every session with no memory of last night.
This journal fixes that: log what happened, ask about it later,
let the memory graph get smarter, and surgically forget a night
you'd rather not remember.
"""

import argparse
import asyncio
import logging
import os

import cognee
from dotenv import load_dotenv

load_dotenv()
cognee.setup_logging(log_level=logging.WARNING)

DATASET = "vegas_night_v3"


def _answer_text(entry) -> str:
    """Pull the human-readable answer out of a recall() response entry."""
    if isinstance(entry, dict):
        return entry.get("text") or str(entry)
    return getattr(entry, "text", None) or str(entry)

_connected = False


async def connect():
    global _connected
    if _connected:
        return
    url = os.environ["COGNEE_CLOUD_URL"]
    api_key = os.environ["COGNEE_CLOUD_API_KEY"]
    await cognee.serve(url=url, api_key=api_key)
    _connected = True


async def cmd_remember(args):
    await connect()
    if args.file:
        result = await cognee.remember(args.file, dataset_name=DATASET)
        print(f"remember() -> ingested file: {args.file}")
    else:
        result = await cognee.remember(args.text, dataset_name=DATASET)
        print(f"remember() -> logged: {args.text}")
    return result


async def cmd_recall(args):
    await connect()
    results = await cognee.recall(query_text=args.question, datasets=[DATASET])
    print(f"\nQ: {args.question}")
    for entry in results:
        print(f"A: {_answer_text(entry)}")
    return results


async def cmd_improve(args):
    await connect()
    try:
        await cognee.improve(dataset=DATASET)
        print("improve() -> memory graph enriched (memify complete)")
    except RuntimeError as e:
        print(f"improve() -> not available on this Cognee Cloud tenant yet ({e})")


async def cmd_forget(args):
    await connect()
    target = args.dataset or DATASET
    await cognee.forget(dataset=target)
    print(f"forget() -> deleted dataset: {target}")


async def cmd_demo(args):
    """A scripted wild-night demo: seed events, enrich, then interrogate the morning after."""
    await connect()

    night = [
        "Doug is the groom. The wedding is Sunday at 4pm in Las Vegas.",
        "Alan brought a tiger back to the hotel room around 3am.",
        "Phil found a baby in the closet the next morning; nobody knows whose it is.",
        "Stu is missing a tooth and secretly married a stripper named Jade at a chapel on the strip.",
        "Stu paid $4,200 for the Caesars Palace suite with his credit card at 2:14am.",
        "Voicemail from Tracy, Doug's fiancee, asking why no one is answering the phone.",
    ]

    print("=== remember(): logging last night ===")
    for fact in night:
        await cognee.remember(fact, dataset_name=DATASET)
        print(f"  + {fact}")

    print("\n=== improve(): enriching the memory graph ===")
    try:
        await cognee.improve(dataset=DATASET)
        print("  done")
    except RuntimeError as e:
        print(f"  skipped -> not available on this Cognee Cloud tenant yet ({e})")

    print("\n=== recall(): the morning after ===")
    questions = [
        "Where is Doug?",
        "What happened with the tiger?",
        "Who got married last night and to whom?",
        "How much did the suite cost?",
    ]
    for q in questions:
        results = await cognee.recall(query_text=q, datasets=[DATASET])
        print(f"\nQ: {q}")
        for entry in results:
            print(f"A: {_answer_text(entry)}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="journal",
        description="Hangover Journal - an AI memory agent powered by Cognee",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_remember = sub.add_parser("remember", help="Log something that happened")
    p_remember.add_argument("text", nargs="?", help="What happened")
    p_remember.add_argument("--file", help="Path to a file/receipt/photo to ingest instead of text")
    p_remember.set_defaults(func=cmd_remember)

    p_recall = sub.add_parser("recall", help="Ask what happened")
    p_recall.add_argument("question")
    p_recall.set_defaults(func=cmd_recall)

    p_improve = sub.add_parser("improve", help="Enrich/prune the memory graph (memify)")
    p_improve.set_defaults(func=cmd_improve)

    p_forget = sub.add_parser("forget", help="Delete a night's memories for good")
    p_forget.add_argument("--dataset", help="Dataset name to delete (defaults to vegas_night)")
    p_forget.set_defaults(func=cmd_forget)

    p_demo = sub.add_parser("demo", help="Run the full remember -> improve -> recall demo with a fictional night")
    p_demo.set_defaults(func=cmd_demo)

    return parser


async def _run(args):
    try:
        await args.func(args)
    finally:
        if _connected:
            await cognee.disconnect()


def main():
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
