# LangChain from Scratch

A hands-on, beginner-friendly intro to [LangChain](https://github.com/langchain-ai/langchain)
— learn the one idea that ties the whole library together (**every component is a
`Runnable`, so you pipe them with `|`**) by running small, heavily commented examples,
then watch that same pipe power a full **RAG** pipeline. Runs on **macOS, Linux, and
Windows**. Verified on **LangChain 1.x**.

## The core idea in one picture

```text
   input (a dict of variables, e.g. {"topic": "..."})
              |
              v
      prompt  ->  model  ->  parser  ->  answer
   (fills in    (the LLM    (turns the raw
    variables)   call)       message into text)

   Every box is a Runnable, so the `|` pipe chains them:
       chain = prompt | model | parser
       chain.invoke({...})  ->  answer

   RAG is the SAME pipe -- with a retriever spliced in front of the prompt:
       {"context": retriever | format_docs, "question": passthrough}
           |  prompt  |  model  |  parser  ->  grounded answer
```

- **Runnable** — the standard interface every component implements (`prompt`, `model`,
  `parser`, `retriever`, ...). Because they all speak the same interface, `|` composes
  them regardless of provider (OpenAI, Anthropic, Gemini, ...).
- **LCEL** — the "LangChain Expression Language": the `|` pipe you use to wire Runnables
  left-to-right into a **chain**.
- **RAG is not a new paradigm** — it's the exact same chain, with a **retriever** that
  looks up relevant document chunks and feeds them in as `context`.

## Setup — from zero to running

This walks a brand-new machine from nothing to every example running. Run the commands
after you've `cd`-ed into the `langchain-basics` folder. Each step shows **both**
macOS/Linux **and** Windows commands — copy the block for your OS.

### 1. Prerequisites

You need **Python 3.11 or newer** and **git**. Check what you have:

```bash
# macOS / Linux
python3 --version    # must be >= 3.11
git --version
```

```powershell
# Windows (PowerShell)
py --version         # must be >= 3.11
git --version
```

> **⚠️ Python version matters — this is the #1 install failure.** LangChain 1.x
> requires **Python ≥ 3.10** (this repo targets **3.11**). If your `python3` is older
> (e.g. 3.9, common as the macOS default), `pip install -r requirements.txt` fails with a
> huge version list and **`ERROR: No matching distribution found for langchain<2.0,>=1.0`**
> — pip is silently filtering out every 1.x release as incompatible with your Python, *not*
> a broken package. Fix: get 3.11 (`brew install python@3.11`, or `pyenv install 3.11`, or
> just use `uv` which fetches it for you) and build the venv with it explicitly — see the
> `python3.11` note in step 3 and [Troubleshooting](#7-troubleshooting).

> **Heads-up (read before class):** this repo installs `sentence-transformers`, which
> pulls in CPU **`torch` (~1–2 GB, several minutes to download, needs internet)** — much
> heavier than a typical LangChain install. On top of that, the **first** index build
> downloads a **~80 MB embedding model** into your HuggingFace cache
> (`~/.cache/huggingface`, outside this repo). **Presenters: install the deps AND
> pre-build the FAISS index the night before, on real internet — never live in front of
> the room.** Every run after the first is offline and fast.

### 2. Get the code

```bash
git clone https://github.com/takshit12/langchain-basics
cd langchain-basics
```

All remaining commands assume you are inside the `langchain-basics` directory.

### 3. Create the virtual environment and install dependencies

Pick **one** of the two options. Within each, run the block for your OS.

**Option A — [`uv`](https://docs.astral.sh/uv/) (fast, cross-platform):**

```bash
# macOS / Linux
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
uv venv --python 3.11 .venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

**Option B — plain `venv` (no extra tools):**

Use `python3.11` **explicitly** when creating the venv — plain `venv` can't fetch a Python
for you, so a bare `python3` that happens to be 3.9 produces a broken 3.9 venv (see the
warning in step 1). If `python3 --version` already reports ≥ 3.11, `python3` is fine too.

```bash
# macOS / Linux
python3.11 -m venv .venv          # or: python3 -m venv .venv  (only if python3 is >= 3.11)
source .venv/bin/activate
python --version                  # confirm it says 3.11.x BEFORE installing
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
py -3.11 -m venv .venv            # the -3.11 selects Python 3.11 explicitly
.venv\Scripts\Activate.ps1
python --version                  # confirm it says 3.11.x
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Heads-up on `pip`:** `python -m venv` (Option B) includes `pip`, but `uv venv`
> (Option A) does **not** — so inside a uv-created venv, `pip install ...` fails with
> `command not found`. Always install with `uv pip install -r requirements.txt` in that
> case (or run `python -m ensurepip --upgrade` once to add `pip`). Using `python -m pip`
> above sidesteps the difference wherever `pip` is present.

On **Windows cmd.exe** (instead of PowerShell), the activation line is
`.venv\Scripts\activate.bat`. If PowerShell blocks activation with an execution-policy
error, see [Troubleshooting](#7-troubleshooting).

Once the venv is **activated** (you'll see `(.venv)` in your prompt), `python` points
inside it, so the rest of this README just uses `python ...` on every OS. (`pip` points
inside it too *if* the venv was made with `python -m venv`; a `uv`-made venv has no `pip`
— see the heads-up above.) Run `deactivate` to exit the venv. The install pulls in `langchain`, `langchain-openai`,
`langchain-community` (still the working FAISS path — see `requirements.txt`),
`langchain-huggingface`, `langchain-text-splitters`, `sentence-transformers`, `faiss-cpu`,
and `python-dotenv`.

### 4. (Optional) Add an API key for the generation step

**Embeddings + FAISS retrieval ALWAYS work with NO key** — they run fully on your
machine. A key is only needed for the final **generation** step (the chat model) in
`rag_demo.py`, `langchain_fundamentals.py`, and `agent_and_middleware.py`. Without a key,
every script falls back gracefully (clearly labeled) instead of crashing.

To enable live generation, copy the template and fill it in:

```bash
# macOS / Linux
cp .env.example .env
```

```powershell
# Windows (PowerShell)
copy .env.example .env
```

Then edit `.env` and set:

```dotenv
OPENROUTER_API_KEY=sk-or-...your-key...
OPENROUTER_MODEL=openai/gpt-4.1-mini
```

Get a key at <https://openrouter.ai/keys> (you may need a small credit balance for live
calls). The scripts call `load_dotenv()`, so they read this automatically. OpenRouter is
reached through `ChatOpenAI(base_url="https://openrouter.ai/api/v1")` — a genuine
LangChain `Runnable`. **`.env` is gitignored** — your key will not be committed.

> **For the live demo, use a real key.** The whole point of `rag_demo.py` is the
> contrast between a plain LLM guessing wrong and RAG answering correctly — that only
> lands with real model answers.

### 5. Verify the install

One line confirms the core imports resolve in your venv (this command is identical on
macOS/Linux and Windows PowerShell):

```bash
python -c "from langchain_core.prompts import ChatPromptTemplate; from langchain_core.output_parsers import StrOutputParser; from langchain_core.runnables import RunnableLambda, RunnablePassthrough; from langchain_core.tools import tool; from langchain_openai import ChatOpenAI; from langchain_huggingface import HuggingFaceEmbeddings; from langchain_text_splitters import RecursiveCharacterTextSplitter; from langchain.agents import create_agent; import faiss; print('core imports OK')"
```

If it prints `core imports OK`, you're ready.

### 6. Run the examples

Run each from the repo root with the venv **activated**. The "What you'll see" note tells
you it worked. There is **no LangGraph-Studio-equivalent step here** — LangChain has no
built-in visual builder, so everything runs on the command line (that's expected, not a
missing piece).

**a. The fundamentals** (self-study; no key required):

```bash
python langchain_fundamentals.py
```

> **What you'll see:** each core building block firing one at a time — the **prompt
> template** filled with a variable, the **output parser** on its own, then the full
> `prompt | model | parser` **LCEL chain** returning a sentence. With no key the model
> step swaps to an offline `RunnableLambda` and the chain returns: *"A Runnable is
> LangChain's standard component interface, which is why prompts, models, and parsers all
> pipe together with `|`."* Finally the `word_counter` **tool** prints its name,
> description, and args schema (with a key, the model returns a `tool_calls` entry asking
> to call it).

**b. Build the FAISS index** (no key required — do this before running `rag_demo.py`):

```bash
python build_rag_index.py --doc docs/kestrel_home_faq.md --index-dir faiss_index
```

> **What you'll see:** the four RAG-build stages print in order — loads the doc, splits it
> into **16 chunks** (`chunk_size=500, chunk_overlap=50`), prints a couple of **sample
> chunks** so you see splitting concretely, embeds them **locally** with
> `all-MiniLM-L6-v2` (the first run downloads the ~80 MB model), and saves the index to
> `faiss_index/`. Build the **swap-doc** index the same way (it splits into **5 chunks**):
>
> ```bash
> python build_rag_index.py --doc docs/meridian_library_policy.md --index-dir faiss_index_library
> ```

**c. The live RAG demo** (Section 5 — use a real key for the full effect):

```bash
python rag_demo.py
```

> **What you'll see:** for each question it runs the **plain LLM first, then full RAG**.
> The plain LLM has never seen the Kestrel Home doc, so it answers *confidently wrong*
> (e.g. "a standard 25% restocking fee after 30 days"); RAG then **retrieves the real
> chunk** — the one containing "**12% restocking fee**" — prints it, and answers **12%**.
> Retrieval always works offline; only generation needs a key (without one, plain mode
> shows a labeled canned wrong answer and RAG shows the retrieved chunks + the top chunk
> verbatim). Run `python rag_demo.py < /dev/null` (macOS/Linux) or
> `python rag_demo.py < NUL` (Windows) for a headless scripted auto-demo. See
> [`rag_demo.py` controls](#rag_demopy-controls) below.

**d. Agent + middleware** (bonus — *not* part of the live walkthrough):

```bash
python agent_and_middleware.py
```

> **What you'll see:** `create_agent(...)` assembles a model + tool + middleware, then
> prints its assembled shape: agent type `CompiledStateGraph` (proof that `create_agent`
> is **built on LangGraph internally**), tools `['get_word_length']`, middleware
> `['ModelRetryMiddleware']`, and graph nodes
> `['__start__', 'model', 'tools', '__end__']`. Without a key it prints structure only
> (no live call); with a key it also invokes the agent and prints the final answer.

### 7. Troubleshooting

- **`ERROR: No matching distribution found for langchain<2.0,>=1.0`** (pip prints a giant
  list of old `0.0.x`–`0.3.x` versions and stops at ~`0.4.0.dev0`). **Your venv is on too
  old a Python** — almost always **3.9**, the macOS default. LangChain 1.x needs Python
  ≥ 3.10, so pip filters out every 1.x release and shows only the 0.x line. A tell: the same
  error mentions `pip version 21.2.4`, the pip bundled with Python 3.9. Changing the command
  (`pip` → `python -m pip` → `python3 -m pip`) won't help — they're all the same interpreter.
  **Fix:** rebuild the venv on 3.11:
  ```bash
  deactivate; rm -rf .venv
  brew install python@3.11               # or: pyenv install 3.11
  python3.11 -m venv .venv               # note: python3.11, NOT python3
  source .venv/bin/activate
  python --version                       # must say 3.11.x
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  ```
  (Or skip the Python chore entirely with `uv`, which fetches 3.11 for you — see Option A.)
  Verify success: `python -c "import langchain; print(langchain.__version__)"` → `1.x`.
- **`pip: command not found` (or `zsh: command not found: pip`) after activating the venv.**
  Your venv was created by `uv venv` (Option A), which doesn't seed `pip`. Install with
  `uv pip install -r requirements.txt` instead, or add pip once with
  `python -m ensurepip --upgrade`. (`python -m pip install ...` also works whenever pip is present.)
- **`torch` install is slow / huge.** Expected — `sentence-transformers` pulls in CPU
  `torch` (~1–2 GB, several minutes). Do it once, on real internet, ahead of time.
- **First run of `build_rag_index.py` hangs on "Embedding chunks".** It's downloading the
  ~80 MB embedding model into `~/.cache/huggingface`. Needs internet the first time only;
  every run afterward is offline and fast.
- **`No index found at 'faiss_index/'`** when running `rag_demo.py`. You skipped the
  build step — run `python build_rag_index.py --doc docs/kestrel_home_faq.md --index-dir faiss_index`
  first.
- **PowerShell won't activate the venv** ("running scripts is disabled on this system").
  Loosen the policy for the current shell only, then re-run activation:
  `Set-ExecutionPolicy -Scope Process RemoteSigned`. (Or use cmd.exe with
  `.venv\Scripts\activate.bat`.)
- **`401 - User not found` / `AuthenticationError` on a generation step.** Your
  `OPENROUTER_API_KEY` is invalid, revoked, or expired — mint a fresh one at
  <https://openrouter.ai/keys> and paste it into `.env`. The scripts detect this and print a
  clean `[live … failed: 401 auth error …]` line, then continue with their labeled offline
  fallback — they never crash. (Other generation errors — `402` no credits, timeouts,
  empty responses — degrade the same way.)
- **`langchain-community` sunset DeprecationWarning.** Expected and intentionally
  suppressed in the FAISS scripts — it's still the canonical FAISS/TextLoader path in
  LangChain 1.x. See the note in `requirements.txt`.

## The examples

| File | Run | Teaches |
|---|---|---|
| `langchain_fundamentals.py` | `python langchain_fundamentals.py` | The core building blocks: **Prompt Template**, **Output Parser**, the `prompt \| model \| parser` **LCEL chain**, and a `@tool` + `bind_tools`. No key needed — the model step swaps to an offline `Runnable`. |
| `build_rag_index.py` | `python build_rag_index.py --doc docs/kestrel_home_faq.md --index-dir faiss_index` | The **first half of RAG**: load → split → embed → store. Fully local, no key. Pre-run before class. |
| `rag_demo.py` | `python rag_demo.py` | **THE live demo.** Plain-LLM (wrong) vs full-RAG (grounded) on a private document, printing the retrieved chunks that changed the answer. |
| `agent_and_middleware.py` | `python agent_and_middleware.py` | **Bonus — not part of the live walkthrough.** `create_agent` = model + tool + middleware in a few lines, compiled to a LangGraph `CompiledStateGraph`. |

> `rag_demo.py` also runs headless (`python rag_demo.py < /dev/null` on macOS/Linux,
> `python rag_demo.py < NUL` on Windows) as a scripted auto-demo.

### `rag_demo.py` controls

Type a bare question to run the **Section 5 run-of-show** (plain first, then RAG), or use
a `:command`:

- `<a question>` — run **plain** first, then **RAG** (plain = "before", RAG = "after")
- `:plain <question>` — run ONLY the plain-LLM answer
- `:rag <question>` — run ONLY the RAG answer
- `:index <dir>` — switch index dir (e.g. `:index faiss_index_library` for the swap doc)
- `:chunks` — reprint the chunks retrieved by the last RAG run
- `:help` — reprint the command help
- `:q` / `quit` / `exit` — leave

## Optional: RAG with a UI

Prefer to *see* retrieval instead of reading it scroll past in a terminal? Two
optional apps wrap the exact same LCEL RAG chain in a UI. They're **standalone**
(they don't import `rag_demo.py`) and need the FAISS index(es) built first.

The UI dependencies (`streamlit`, `chainlit`) are already included in
`requirements.txt`, so if you ran the install in step 3 you're ready. (Installing
them separately: `uv pip install streamlit chainlit`.)

- **`rag_app.py` — Streamlit (recommended).** A sidebar to pick the index
  (Kestrel Home / Meridian Library), a top-k slider, and a toggle for the plain
  "before" answer; the main pane shows each retrieved chunk in its own expander
  titled with its similarity score, then the grounded RAG answer.

  ```bash
  streamlit run rag_app.py
  ```

- **`rag_chat.py` — Chainlit (chat-style variant).** The same chain in a chat
  window: it streams the grounded answer and sends the retrieved chunks (with
  scores) as a collapsible step.

  ```bash
  chainlit run rag_chat.py -w
  ```

> **What you'll see:** the retrieved chunks with their similarity scores next to
> the grounded answer — the plain LLM guesses *25%*, RAG retrieves the "**12%
> restocking fee**" chunk and answers **12%**. Retrieval is 100% local; only the
> generated answer needs a key (without one, both apps still show the chunks and
> fall back to a labeled extractive top-chunk).

### `build_rag_index.py` flags

- `--doc <path>` — the source text document (default `docs/kestrel_home_faq.md`)
- `--index-dir <dir>` — where to write the FAISS index (default `faiss_index`)

Build both indexes so `rag_demo.py`'s `:index` swap works:

```bash
python build_rag_index.py --doc docs/kestrel_home_faq.md      --index-dir faiss_index
python build_rag_index.py --doc docs/meridian_library_policy.md --index-dir faiss_index_library
```

## API surface used here

| Call | What it does |
|---|---|
| `a \| b \| c` (LCEL) | pipe Runnables left-to-right into a **chain**; each output feeds the next input |
| `ChatPromptTemplate.from_template(...)` | reusable prompt with `{variables}` filled at `.invoke()` time |
| `ChatOpenAI(model=..., base_url=..., api_key=...)` | a chat-model Runnable; the `base_url="https://openrouter.ai/api/v1"` trick points it at OpenRouter |
| `StrOutputParser()` | turn the model's raw message into a plain string (the last link in the chain) |
| `@tool` + `model.bind_tools([...])` | expose a Python function to the model so it can decide to call it |
| `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)` | split a document into overlapping chunks for precise retrieval |
| `HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")` | turn text chunks into vectors **locally**, no API key |
| `FAISS.from_documents(chunks, embeddings)` / `.save_local(dir)` / `.load_local(dir, ...)` | build, persist, and reload a local vector store (from `langchain_community.vectorstores`) |
| `store.as_retriever(search_kwargs={"k": 3})` | wrap the vector store as a **retriever** Runnable you can splice into a chain |
| `RunnablePassthrough()` | pass the input through unchanged — used to route the question into the RAG chain alongside `context` |
| `create_agent(model=..., tools=[...], middleware=[...])` | assemble a full agent loop in one call; returns a LangGraph `CompiledStateGraph` |
| `ModelRetryMiddleware(max_retries=..., backoff_factor=...)` | built-in middleware that auto-retries failed model calls — a hook into the agent loop |
