import json
import os
import time
import urllib.error
import urllib.request
from itertools import cycle

DEFAULT_GROQ_MODEL = os.getenv("STARLIGHT_GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are Starlight's upgrade tutor. Answer naturally, clearly, and briefly.
Be friendly, direct, useful, and never pretend to have memories or abilities you do not have.
For identity questions, say you are Starlight, a local AI assistant that can chat, learn saved Q&A, remember user facts, and solve math.
For math, show concise steps when helpful.
If the user gives a tiny fragment, ask one specific follow-up instead of generic filler."""

TRAINING_TOPICS = [
    "friendly greetings and first messages",
    "assistant identity and creator questions",
    "what the assistant can do",
    "short confused replies like idk or i don't know",
    "math help requests and examples",
    "learning command examples",
    "memory command examples",
    "planning and brainstorming help",
    "simple science explanations",
    "safe coding help",
]

class GroqProvider:
    def __init__(self, api_key=None, model=None, timeout=25):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or DEFAULT_GROQ_MODEL
        self.timeout = timeout

    @property
    def enabled(self):
        return bool(self.api_key)

    def chat(self, user_message, history=None):
        if not self.enabled:
            return None
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in (history or [])[-6:]:
            messages.append({"role": "user", "content": turn.get("user", "")})
            messages.append({"role": "assistant", "content": turn.get("bot", "")})
        messages.append({"role": "user", "content": user_message})
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0.55,
            "max_tokens": 500,
        }).encode("utf-8")
        request = urllib.request.Request(
            GROQ_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, json.JSONDecodeError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            return None

    def generate_training_pair(self, topic, learned_count):
        prompt = (
            "Generate exactly one useful training pair for Starlight's local knowledge base. "
            "Return ONLY valid JSON with keys question and answer. "
            "The question should be a likely user message; the answer should be natural, specific, under 70 words, and useful. "
            "Avoid duplicates and improve weak chatbot behavior. "
            f"Topic: {topic}. Previously learned this run: {learned_count}."
        )
        raw = self.chat(prompt)
        if not raw:
            raise RuntimeError("Groq returned no training data")
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Groq response did not contain a JSON object")
        data = json.loads(raw[start:end + 1])
        question = str(data.get("question", "")).strip()
        answer = str(data.get("answer", "")).strip()
        if not question or not answer:
            raise ValueError("Groq training JSON missing question or answer")
        return question, answer


def run_training_session(knowledge_engine, provider, progress_callback=None, max_errors=10, max_cycles=None):
    stats = {
        "topics": 0,
        "learned": 0,
        "errors": 0,
        "provider": "Groq",
        "status": "training",
        "stop_reason": "manual stop",
    }
    if not provider.enabled:
        stats["errors"] = max_errors + 1
        stats["status"] = "stopped"
        stats["stop_reason"] = "missing GROQ_API_KEY"
        if progress_callback:
            progress_callback(dict(stats))
        return stats

    topic_stream = cycle(TRAINING_TOPICS)
    try:
        while stats["errors"] <= max_errors:
            if max_cycles is not None and stats["topics"] >= max_cycles:
                stats["status"] = "stopped"
                stats["stop_reason"] = "cycle limit reached"
                break
            topic = next(topic_stream)
            stats["topics"] += 1
            try:
                question, answer = provider.generate_training_pair(topic, stats["learned"])
                existing, conf = knowledge_engine.query_semantic_match(question)
                if existing is None or conf < 0.98:
                    knowledge_engine.learn(question, answer)
                    stats["learned"] += 1
                    stats["last_question"] = question[:70]
                stats["status"] = "training"
            except Exception as exc:
                stats["errors"] += 1
                stats["last_error"] = str(exc)[:70]
                if stats["errors"] > max_errors:
                    stats["status"] = "stopped"
                    stats["stop_reason"] = "more than 10 errors"
                    break
            if progress_callback:
                progress_callback(dict(stats))
            time.sleep(0.18)
    except KeyboardInterrupt:
        stats["status"] = "stopped"
        stats["stop_reason"] = "manual stop"
    return stats
