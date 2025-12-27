import os
import json
import re
import html
import requests
import numpy as np
from sentence_transformers import SentenceTransformer


API_KEY = "YOUR KEY"
MODEL_NAME = "MODEL NAME"
EMBED_MODEL = "MODEL NAME"

embedder = SentenceTransformer(EMBED_MODEL)


def normalize_query(q: str) -> str:
    q = q.lower()
    q += "?"
    slang = {
        "slang_word1": "meaning1",
      ...
    }
  
    for k, v in slang.items():
        q = q.replace(k, v)
    return q.strip()

def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\[/?(out|output|response|assistant).*?\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^out:?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 1200:
        text = text[:1200].strip() + "..."
    return text or "Couldn't find anything"

def load_chunks(file="custom_data.txt", max_len=1800):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        text = f.read().strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_len:
            current += " " + s
        else:
            chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks


if os.path.exists("embeddings.npy") and os.path.exists("chunks.json"):
    embeddings = np.load("embeddings.npy")
    with open("chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
else:
    chunks = load_chunks()
    passages = [f"passage: {t}" for t in chunks]
    embeddings = embedder.encode(passages)
    np.save("embeddings.npy", embeddings)
    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)


def find_relevant_context(query, top_k=3, threshold=0.35):
    q_emb = embedder.encode([f"query: {query}"])[0]
    sims = np.dot(embeddings, q_emb) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(q_emb))
    top_idx = np.argsort(sims)[-top_k:][::-1]
    selected = [chunks[i] for i in top_idx if sims[i] > threshold]
    return "\n\n".join(selected) if selected else "Coudln't find any info."


async def gpt_request(user_input: str) -> str:
    query = normalize_query(user_input)
    context = find_relevant_context(query)

    system_prompt = (
        '''your prompt for the ai to be special assistant'''
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "max_tokens": 1500,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(
            "https://...", #your link
            headers=headers,
            data=json.dumps(payload),
            timeout=40
        )


        if r.status_code != 200:
            return "Server error."

        data = r.json()
        ans = data["choices"][0]["message"]["content"]
        return clean_text(ans)

    except Exception as e:
        return f"Error: {type(e).__name__} — {e}"



