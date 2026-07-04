"""
rag_app.py  --  a STREAMLIT UI for the RAG demo, so the room can SEE retrieval.

This is the visual companion to `rag_demo.py`. Same idea, same LCEL chain shape,
but now the retrieved chunks (the load-bearing part of RAG) are shown on screen,
each in its own expander titled with its similarity score, so a room can watch
retrieval do its job instead of reading it scroll past in a terminal.

    plain LLM  ->  confidently WRONG (never saw the private doc)
    RAG        ->  {"context": retriever | format_docs, "question": passthrough}
                       | prompt | model | parser  ->  grounded, CORRECT answer

WHAT NEEDS A KEY, WHAT DOESN'T
  - Embedding + FAISS retrieval ALWAYS work locally, with NO API key. The chunks
    (with scores) render even with no key -- retrieval is the point.
  - Only the final GENERATION step (the chat model) needs OPENROUTER_API_KEY.
  - With no key we NEVER crash: instead of a generated answer we show a clearly
    labeled EXTRACTIVE fallback (the top retrieved chunk). Use a real key in the
    live session -- the hallucination-vs-grounded contrast is what lands.

This app is deliberately STANDALONE: it does not import from `rag_demo.py`, so it
keeps working even if that script changes. Build the FAISS index(es) first:
    .venv/bin/python build_rag_index.py --doc docs/kestrel_home_faq.md \
        --index-dir faiss_index

Run it:
    streamlit run rag_app.py
"""

import logging
import os
import warnings

# Quiet HuggingFace's noisy `\r`-based progress bar and the "unauthenticated
# requests to the HF Hub" notice BEFORE importing HF libs -- same guard the other
# scripts use. Must be set before langchain_huggingface imports huggingface_hub.
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# `langchain-community` (which provides FAISS) prints a "sunset"
# DeprecationWarning at import. It remains the only working FAISS path in
# LangChain 1.x. Suppress the noisy sunset warning; see requirements.txt.
# ---------------------------------------------------------------------------
warnings.filterwarnings(
    "ignore", message=".*langchain-community.*", category=DeprecationWarning
)

import streamlit as st
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

# Pick up OPENROUTER_API_KEY / OPENROUTER_MODEL from the project .env (optional).
load_dotenv()

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384  # all-MiniLM-L6-v2 -> 384-dimensional vectors.

# The selectbox options: label -> index dir. Both indexes are built by
# build_rag_index.py; the Meridian one is the "swap the document" demo.
INDEX_CHOICES = {
    "faiss_index  [Kestrel Home]": "faiss_index",
    "faiss_index_library  [Meridian Library]": "faiss_index_library",
}

# A good default question: the answer (a 12% restocking fee) lives ONLY in the
# Kestrel Home doc, so a plain LLM cannot possibly know it, but RAG can.
DEMO_QUESTION = (
    "What is Kestrel Home's restocking fee on returns outside the 45-day window?"
)


# ---------------------------------------------------------------------------
# The RAG prompt -- same shape as rag_demo.py. It tells the model to answer ONLY
# from the retrieved context and to admit when the context lacks the answer,
# which is what keeps a grounded answer from drifting back into guessing.
# ---------------------------------------------------------------------------
RAG_PROMPT = ChatPromptTemplate.from_template(
    "You are a support assistant. Answer the question using ONLY the context "
    "below. If the context does not contain the answer, say you don't have that "
    "information -- do not guess.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


def short_api_error(exc: Exception) -> str:
    """Turn a noisy API exception into one short, classroom-friendly line."""
    msg = str(exc)
    if "401" in msg or "User not found" in msg or "authentication" in msg.lower():
        return "401 auth error -- your OPENROUTER_API_KEY looks invalid or expired"
    return msg.splitlines()[0][:160]


def format_docs(docs) -> str:
    """Flatten a list of retrieved Documents into one context string."""
    return "\n\n".join(d.page_content for d in docs)


# ---------------------------------------------------------------------------
# Model factory. Returns a real ChatOpenAI Runnable if a key is set, else None.
# (When None, the app shows a clearly-labeled extractive fallback instead.)
# ---------------------------------------------------------------------------
def make_model() -> ChatOpenAI | None:
    """A genuine LangChain Runnable wrapping OpenRouter, or None with no key."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-mini"),
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


# ---------------------------------------------------------------------------
# Cached loaders. st.cache_resource keeps the (heavy) embedding model and each
# FAISS index in memory across reruns -- Streamlit reruns the whole script on
# every widget change, so without this we'd reload the ~80MB model every click.
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading the local embedding model...")
def get_embeddings() -> HuggingFaceEmbeddings:
    """Load the local, no-key embedding model once (all-MiniLM-L6-v2)."""
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


@st.cache_resource(show_spinner="Loading FAISS index...")
def get_store(index_dir: str) -> FAISS | None:
    """Load a persisted FAISS index once, or None if the directory is missing."""
    if not os.path.isdir(index_dir):
        return None
    # allow_dangerous_deserialization: FAISS indexes are pickled; we trust our own.
    return FAISS.load_local(
        index_dir, get_embeddings(), allow_dangerous_deserialization=True
    )


# ---------------------------------------------------------------------------
# The two answer modes, factored out so the page body stays readable.
# ---------------------------------------------------------------------------
def rag_answer(store: FAISS, question: str, k: int, model: ChatOpenAI) -> str:
    """The exact LCEL RAG chain from rag_demo.py -- retriever piped into the
    prompt, the model, and an output parser. Same `|` pattern as Section 1."""
    retriever = store.as_retriever(search_kwargs={"k": k})
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | model
        | StrOutputParser()
    )
    return chain.invoke(question).strip()


def plain_answer(question: str, model: ChatOpenAI) -> str:
    """The plain LLM, no retrieval -- the 'before'. Watch it invent specifics."""
    return (model | StrOutputParser()).invoke(question).strip()


# ---------------------------------------------------------------------------
# Page.
# ---------------------------------------------------------------------------
st.set_page_config(page_title="RAG, visualized", page_icon="🔎", layout="wide")

st.title("🔎 RAG, visualized")
st.markdown(
    "**RAG** = retrieve the relevant document chunks first, then let the LLM "
    "answer **grounded in them** instead of guessing from memory."
)
st.caption(
    "Embedding + retrieval run **locally with no API key** -- only the final "
    "generation step needs `OPENROUTER_API_KEY`. Watch the same question go from "
    "*confidently wrong* (plain LLM) to *grounded and correct* (RAG)."
)

model = make_model()

# --- Sidebar: the controls -------------------------------------------------
with st.sidebar:
    st.header("Controls")

    index_label = st.selectbox(
        "Index (document)",
        options=list(INDEX_CHOICES.keys()),
        index=0,
        help="Which prebuilt FAISS index to retrieve from.",
    )
    index_dir = INDEX_CHOICES[index_label]

    k = st.slider(
        "Top-k chunks to retrieve",
        min_value=1,
        max_value=6,
        value=3,
        help="How many of the most similar chunks to pull in as context.",
    )

    show_plain = st.checkbox(
        "Also show the plain LLM answer (the before)",
        value=True,
        help="Show the ungrounded answer side by side, so the contrast is visible.",
    )

    st.divider()

    # Load the store now so we can show the index stats in the sidebar.
    store = get_store(index_dir)
    if store is None:
        st.error(
            f"No index at `{index_dir}/`. Build it first (no key needed):\n\n"
            f"`.venv/bin/python build_rag_index.py --index-dir {index_dir}`"
        )
    else:
        st.metric("Vectors in index", store.index.ntotal)
        st.metric("Embedding dim", EMBED_DIM)
        st.caption(f"Model: `all-MiniLM-L6-v2`  |  index: `{index_dir}/`")

    st.divider()
    if model is None:
        st.warning(
            "No `OPENROUTER_API_KEY` set -- retrieval still works and chunks "
            "still render; the answer falls back to an extractive top-chunk."
        )
    else:
        st.success("Live generation is ON (OPENROUTER_API_KEY detected).")

# --- Main: the question ----------------------------------------------------
question = st.text_input(
    "Ask a question about the selected document",
    value=DEMO_QUESTION,
    placeholder="e.g. What is the restocking fee on late returns?",
)
ask = st.button("Ask", type="primary")

# Fire on the button OR on Enter (a non-empty text_input submits on Enter, which
# reruns the script; we answer whenever there's a question and an index).
if (ask or question) and question.strip():
    if store is None:
        st.stop()  # the sidebar already showed the build-the-index hint.

    # 1. RETRIEVE -- always local, always works. similarity_search_with_score
    # gives us the score to title each expander with. Lower L2 distance = closer.
    scored = store.similarity_search_with_score(question, k=k)

    st.subheader(f"1. Retrieved {len(scored)} chunks  (retrieval is 100% local)")
    st.caption(
        "Each chunk with its similarity score (FAISS L2 distance -- **lower is "
        "closer**). This is *why* the grounded answer changes."
    )
    for i, (doc, score) in enumerate(scored):
        with st.expander(f"chunk[{i}]  ·  score {score:.4f}", expanded=(i == 0)):
            st.write(doc.page_content.strip())

    st.divider()

    # 2. ANSWER -- grounded (RAG) prominently, plain (optional) alongside.
    if show_plain:
        rag_col, plain_col = st.columns(2)
    else:
        rag_col = st.container()
        plain_col = None

    with rag_col:
        st.subheader("2. RAG answer  (grounded ✅)")
        if model is None:
            st.info("Extractive fallback (no key) -- the top retrieved chunk:")
            top = scored[0][0].page_content.strip().replace("\n", " ")
            st.write(f"{top[:200]}...")
            st.caption(
                "With a key, the chat model reads ALL the chunks above and "
                "answers in one grounded sentence."
            )
        else:
            with st.spinner("Generating the grounded answer..."):
                try:
                    st.success(rag_answer(store, question, k, model))
                except Exception as exc:  # never hard-fail the UI.
                    st.error(f"Live generation failed: {short_api_error(exc)}")
                    top = scored[0][0].page_content.strip().replace("\n", " ")
                    st.info(f"Extractive fallback -- top chunk:\n\n{top[:200]}...")

    if plain_col is not None:
        with plain_col:
            st.subheader("2. Plain LLM answer  (ungrounded ⚠️)")
            st.caption("The 'before' -- no document access, so it guesses.")
            if model is None:
                st.info(
                    "Illustrative 'confidently wrong' answer a plain LLM might "
                    "give (shown because no key is set):"
                )
                st.write(
                    '"Kestrel Home charges a standard 25% restocking fee on all '
                    'returns after 30 days." -- made up; the real fee is 12%.'
                )
            else:
                with st.spinner("Generating the plain answer..."):
                    try:
                        st.warning(plain_answer(question, model))
                    except Exception as exc:  # never hard-fail the UI.
                        st.error(f"Live call failed: {short_api_error(exc)}")
