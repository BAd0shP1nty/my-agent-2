"""RAG Engine for Telecom ITSM Knowledge Base.

Embeddings: OpenAI text-embedding-3-small (1536 dim)
Vector Database: FAISS (faiss-cpu)
LLM: DeepSeek (deepseek-chat)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

import faiss
import numpy as np
from openai import OpenAI

from knowledge_base import get_chunks


class TelecomRAGEngine:
    """Manages document chunking, FAISS indexing, similarity retrieval, and DeepSeek synthesis."""

    def __init__(
        self,
        openai_api_key: str = "",
        deepseek_api_key: str = "",
        deepseek_base_url: str = "https://api.deepseek.com",
        deepseek_model: str = "deepseek-chat",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.openai_api_key = openai_api_key.strip()
        self.deepseek_api_key = deepseek_api_key.strip()
        self.deepseek_base_url = deepseek_base_url.strip() or "https://api.deepseek.com"
        self.deepseek_model = deepseek_model.strip() or "deepseek-chat"
        self.embedding_model = embedding_model.strip() or "text-embedding-3-small"

        self.chunks = get_chunks()
        self.index: faiss.IndexFlatIP | None = None
        self.embeddings: np.ndarray | None = None
        self.is_openai_embedded: bool = False

        self._build_index()

    def _get_openai_embeddings(self, texts: list[str]) -> np.ndarray:
        """Fetch embeddings from OpenAI text-embedding-3-small."""
        client = OpenAI(api_key=self.openai_api_key)
        response = client.embeddings.create(
            input=texts,
            model=self.embedding_model,
        )
        data = [item.embedding for item in response.data]
        arr = np.array(data, dtype=np.float32)
        # L2 normalize for cosine similarity via inner product (IndexFlatIP)
        faiss.normalize_L2(arr)
        return arr

    def _get_fallback_embeddings(self, texts: list[str]) -> np.ndarray:
        """Deterministic pseudo-embedding fallback when OPENAI_API_KEY is not provided.
        
        Uses character and n-gram hash projections (dim 1536) to allow local verification
        without crashing if the user hasn't configured OpenAI embeddings yet.
        """
        dim = 1536
        vectors = []
        for text in texts:
            words = re.findall(r"\w+", text.lower())
            vec = np.zeros(dim, dtype=np.float32)
            for w in words:
                h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
                idx = h % dim
                sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        arr = np.array(vectors, dtype=np.float32)
        return arr

    def _build_index(self):
        """Build and populate the FAISS index."""
        texts = [chunk["text"] for chunk in self.chunks]

        if self.openai_api_key:
            try:
                self.embeddings = self._get_openai_embeddings(texts)
                self.is_openai_embedded = True
            except Exception as e:
                # If OpenAI quota/key fails, gracefully fall back to local hash vectorizer
                self.embeddings = self._get_fallback_embeddings(texts)
                self.is_openai_embedded = False
        else:
            self.embeddings = self._get_fallback_embeddings(texts)
            self.is_openai_embedded = False

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Retrieve top_k matching chunks from FAISS."""
        if self.index is None or self.embeddings is None:
            self._build_index()

        if self.is_openai_embedded and self.openai_api_key:
            try:
                q_vec = self._get_openai_embeddings([query])
            except Exception:
                q_vec = self._get_fallback_embeddings([query])
        else:
            q_vec = self._get_fallback_embeddings([query])

        scores, indices = self.index.search(q_vec, min(top_k, len(self.chunks)))
        
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx != -1 and idx < len(self.chunks):
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                chunk["rank"] = rank
                results.append(chunk)
        return results

    def answer_query(self, query: str, top_k: int = 4) -> dict[str, Any]:
        """Execute RAG pipeline: Retrieve context and generate grounded response via DeepSeek."""
        retrieved_chunks = self.retrieve(query, top_k=top_k)

        # Assemble context
        context_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            header = f"[Source {idx} | ID: {chunk['id']} | Page: {chunk['page']} | Title: {chunk['title']}]"
            context_parts.append(f"{header}\n{chunk['text']}")
        context_text = "\n\n".join(context_parts)

        # Strict grounding prompt
        system_prompt = (
            "You are an expert Telecom Operations and IT Service Management (ITSM) AI Assistant.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. Answer the question ONLY using the factual information contained in the PROVIDED CONTEXT below.\n"
            "2. Do NOT use outside knowledge, assumptions, or hallucinations. If the question cannot be directly and fully "
            "answered from the context, state explicitly: 'I cannot answer this question based on the provided Telecom ITSM knowledge base because [briefly state what information is missing]'.\n"
            "3. Cite the exact sources used in your answer, including the Incident ID (e.g., TEL-INC-2026-0003), "
            "Runbook ID (e.g., RB-ITSM-02), Subsystem name, or Page number.\n"
            "4. Structure your response clearly with headings or bullet points for readability."
        )

        user_prompt = (
            f"PROVIDED CONTEXT FROM TELECOM ITSM DOCUMENT:\n"
            f"--------------------------------------------------\n"
            f"{context_text}\n"
            f"--------------------------------------------------\n\n"
            f"USER QUESTION: {query}\n\n"
            f"Please answer strictly according to the context provided above:"
        )

        if not self.deepseek_api_key:
            return {
                "answer": (
                    "⚠️ **DeepSeek API Key Missing**: Please provide your DeepSeek API key in `.streamlit/secrets.toml` "
                    "or in the sidebar to generate answers with `deepseek-chat`.\n\n"
                    "Below are the retrieved context chunks from the FAISS database that match your query:"
                ),
                "retrieved_chunks": retrieved_chunks,
                "is_grounded": True,
                "embedding_provider": "OpenAI text-embedding-3-small" if self.is_openai_embedded else "Local Hash Vectorizer (Provide OpenAI key for text-embedding-3-small)",
            }

        try:
            client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
            )
            response = client.chat.completions.create(
                model=self.deepseek_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # Low temperature for deterministic, factual grounding
            )
            answer_text = response.choices[0].message.content or "No response generated."
            
            # Check if answer indicates refusal / ungrounded request
            is_refusal = (
                "cannot answer" in answer_text.lower()
                or "not mentioned in the provided context" in answer_text.lower()
                or "does not contain" in answer_text.lower()
            )

            return {
                "answer": answer_text,
                "retrieved_chunks": retrieved_chunks,
                "is_grounded": not is_refusal,
                "is_refusal": is_refusal,
                "embedding_provider": "OpenAI text-embedding-3-small" if self.is_openai_embedded else "Local Hash Vectorizer (Provide OpenAI key for text-embedding-3-small)",
            }

        except Exception as err:
            return {
                "answer": f"❌ **Error calling DeepSeek API ({self.deepseek_model})**: {str(err)}",
                "retrieved_chunks": retrieved_chunks,
                "is_grounded": False,
                "embedding_provider": "OpenAI text-embedding-3-small" if self.is_openai_embedded else "Local Hash Vectorizer",
            }
