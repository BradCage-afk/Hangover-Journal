# Hangover Journal

*Built for [WeMakeDevs x Cognee — "The Hangover Part AI: Where's My Context?"](https://wemakedevs.org)*

## The problem

LLM calls are stateless. Every session your AI wakes up with no memory of what happened the
night (or session) before — it forgets who the groom was, loses the receipts, and has no
idea whose baby that is in the closet.

## The solution

**Hangover Journal** is a memory agent built entirely on [Cognee](https://www.cognee.ai)'s
hybrid graph-vector memory layer. Log events as they happen (text, receipts, voicemails),
then ask about them later — across infinite sessions, with zero amnesia. When a night is
better left forgotten, delete it for good.

It's a thin, deliberately small CLI so the four Cognee lifecycle operations are the whole
story:

| Command | Cognee call | What it does |
|---|---|---|
| `remember` | `cognee.remember()` | Ingests a fact, receipt, or file into the knowledge graph |
| `recall` | `cognee.recall()` | Asks a question; Cognee routes between vector similarity and graph traversal |
| `improve` | `cognee.improve()` | Runs memify — enriches and reweights the graph after ingestion |
| `forget` | `cognee.forget()` | Surgically deletes a dataset (a "night") for good |

## Demo

```bash
uv run python3 main.py demo
```

This seeds a fictional wild night, enriches the memory, then asks:

```
Q: Where is Doug?
A: Doug is at his wedding in Las Vegas.

Q: What happened with the tiger?
A: Alan brought a tiger back to his hotel room around 3am, and the tiger was inside the hotel room.

Q: Who got married last night and to whom?
A: Stu married Jade.

Q: How much did last night cost and who paid?
A: The suite cost $4,200, and it was paid with Stu's credit card.
```

No hardcoded answers — every response above comes from Cognee's hybrid graph completion
over the six facts that were `remember()`'d seconds earlier.

## Usage

```bash
# log something that happened
uv run python3 main.py remember "Doug is the groom. The wedding is Sunday at 4pm in Las Vegas."
uv run python3 main.py remember --file receipt.pdf

# ask about it later, in a completely new process/session
uv run python3 main.py recall "Where is Doug?"

# enrich the graph after a batch of ingestion
uv run python3 main.py improve

# wipe a night you'd rather not remember
uv run python3 main.py forget --dataset vegas_night
```

## Setup

Requires Python 3.10+ (this repo pins 3.11 via [uv](https://docs.astral.sh/uv/)).

1. Sign up at [platform.cognee.ai](https://platform.cognee.ai) and grab your tenant URL +
   API key from the API Keys page (hackathon participants: redeem code `COGNEE-35` for the
   free Developer plan).
2. Copy `.env.example` to `.env` and fill in `COGNEE_CLOUD_URL` / `COGNEE_CLOUD_API_KEY`.
3. `uv sync`
4. `uv run python3 main.py demo`

## Known limitation

`cognee.improve()` (memify) currently 404s on the Cognee Cloud beta tenant used for this
build — the call is wired up correctly (see `cmd_improve` in `main.py`) and fails soft with
a clear message rather than crashing, since the endpoint isn't deployed cloud-side yet.
`remember()`, `recall()`, and `forget()` are fully verified end-to-end against Cognee Cloud.

## AI tools disclosure

Built with the help of [Claude Code](https://claude.com/claude-code) (Anthropic) for
scaffolding, debugging, git/GitHub setup, and README drafting. All Cognee integration logic,
API calls, and design decisions were directed and reviewed by the author.

## Why Cognee

This is deliberately not a wrapper around a vector DB with extra steps. Every `recall()`
answer above came back with `"source": "graph"` — Cognee built an actual knowledge graph
from six disconnected sentences and reasoned over entity relationships (Doug → wedding,
Stu → Jade → chapel, Stu's card → the suite charge) to answer natural-language questions
no single sentence answers on its own.

## Credits

Built on [Cognee](https://github.com/topoteretes/cognee), the open-source hybrid
graph-vector memory layer this project's memory lifecycle is powered by.
