"""
Chat assistant for the dashboard (LLM API).

Works with every provider that offers an OpenAI-compatible chat API
(OpenAI, DeepSeek, Mistral, Anthropic compatibility endpoint, local Ollama ...).
Providers are defined in config.py (p["llm_providers"]).

The assistant sees a text summary of the CURRENT dashboard state (selected menus, key figures,
aggregated table, data quality report) - no raw OSM points are sent.

API key (first match wins):
  1. .streamlit/secrets.toml          OPENAI_API_KEY = "sk-..."      (recommended, never commit it!)
  2. environment variable             OPENAI_API_KEY
  3. password field in the sidebar    (kept only in the browser session)
"""
import os

import streamlit as st

SYSTEM_PROMPT = """You are the assistant of a Streamlit dashboard that visualizes OpenStreetMap (OSM) data of Berlin.
Answer the questions of the user about what the dashboard currently shows.

Rules:
- Use ONLY the dashboard data below for numbers and rankings. Do not invent values. If the data does not
  contain the answer, say so and suggest which menu selection in the dashboard would show it.
- The user may have changed the menus since earlier messages: always use the CURRENT data below.
- OSM is crowd-sourced. When interpreting low values or "gaps", remind the user that mapping quality
  differs between areas and that the data quality report should be considered.
- Be concise. Answer in the language of the user."""


# =============================================================================
# Context: what the assistant knows about the dashboard
# =============================================================================
def build_context(src, cat, area_label, ind, mtype, key, pts_f, agg, quality):
    """Text summary of the current dashboard state"""
    tbl = agg.drop(columns="geometry")[[key, "count", "area_km2", "Einwohner", "value"]].copy()
    tbl["area_km2"] = tbl["area_km2"].round(2)
    tbl = tbl.sort_values("value", ascending=False, na_position="last")

    lines = [
        "CURRENT DASHBOARD STATE",
        "Data source: " + str(src) + " (OpenStreetMap, Berlin)",
        "Category filter: " + str(cat),
        "Area unit: " + str(area_label),
        "Indicator: " + str(ind) + "   (column 'value' in the table)",
        "Map type: " + str(mtype),
        "Objects shown: " + str(len(pts_f)),
        "Areas without any object: " + str(int((agg["count"] == 0).sum())) + " of " + str(len(agg)),
        "",
        "DATA QUALITY REPORT (complete data source, without category filter)",
        quality.to_csv(index=False, sep=";"),
        "AGGREGATED TABLE (one row per area; count = number of objects, Einwohner = residents,",
        "value = selected indicator, empty = not defined)",
        tbl.to_csv(index=False, sep=";"),
    ]
    return "\n".join(lines)


# =============================================================================
# API key and client
# =============================================================================
def _secret(name):
    """Key from .streamlit/secrets.toml or environment variable (None if not found)"""
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:          # no secrets file
        pass
    return os.environ.get(name)


def _stream_answer(client, model, messages, max_tokens):
    """Generator with the text chunks of the answer (for st.write_stream)"""
    stream = client.chat.completions.create(model=model, messages=messages, stream=True,
                                            temperature=0.2, max_tokens=max_tokens)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# =============================================================================
# UI
# =============================================================================
def render_chat(context, pdict):
    """Chat panel (main area) + LLM settings (sidebar). Call at the end of the app."""
    providers = pdict["llm_providers"]

    # ---- settings in the sidebar -------------------------------------------
    with st.sidebar.expander("Chat assistant (LLM settings)"):
        names    = list(providers.keys())
        provider = st.selectbox("Provider", names, index=names.index(pdict["llm_default"]), key="llm_provider")
        spec     = providers[provider]
        model    = st.text_input("Model", spec["model"], key="llm_model_" + provider)
        base_url = st.text_input("Base URL", spec["base_url"], key="llm_url_" + provider,
                                 disabled=not spec.get("editable_url", False))
        api_key  = _secret(spec["secret"])
        if api_key:
            st.caption("API key found (" + spec["secret"] + ").")
        else:
            api_key = st.text_input("API key", type="password", key="llm_key_" + provider,
                                    help="Or set " + spec["secret"] + " in .streamlit/secrets.toml")
        st.caption("Sent to the provider: your question and the aggregated numbers of the dashboard.")

    # ---- chat panel ---------------------------------------------------------
    st.divider()
    head, clear = st.columns([5, 1])
    head.subheader("Chat assistant")
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if clear.button("Clear chat"):
        st.session_state["chat_messages"] = []

    if not api_key:
        st.info("To use the chat, enter an API key in the sidebar (Chat assistant) or put it in "
                ".streamlit/secrets.toml.")
    else:
        st.caption("Ask about the current view, e.g. \"Which three areas have the highest value?\" or "
                   "\"What do the data quality results mean for my conclusions?\"  ·  Model: " + provider + " / " + model)

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about the data ...", disabled=not api_key)
    if not question:
        return

    st.session_state["chat_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    try:
        from openai import OpenAI
    except ImportError:
        st.error("Package 'openai' is missing:  pip install openai")
        return

    history  = st.session_state["chat_messages"][-pdict["llm_max_history"]:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}] + history
    with st.chat_message("assistant"):
        try:
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=60)
            answer = st.write_stream(_stream_answer(client, model, messages, pdict["llm_max_tokens"]))
        except Exception as e:                       # wrong key, no credit, wrong model, network ...
            answer = None
            st.session_state["chat_messages"].pop()      # question stays unanswered -> do not keep it
            st.error("The LLM request failed: " + type(e).__name__ + " - " + str(e)[:300])
    if answer:
        st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
