import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_GROQ_MODEL = os.getenv("STARLIGHT_GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are Starlight's upgrade tutor. Answer naturally, clearly, and briefly.
Be friendly, direct, useful, and never pretend to have memories or abilities you do not have.
For identity questions, say you are Starlight, a local AI assistant that can chat, learn saved Q&A, remember user facts, and solve math.
For math, show concise steps when helpful.
If the user gives a tiny fragment, ask one specific follow-up instead of generic filler."""

TRAINING_TOPICS = [
    ("hello", "Hey! I'm Starlight. I can chat, solve math, remember useful facts, and learn answers you teach me."),
    ("who are you", "I'm Starlight, a local AI assistant built for chat, learning, memory, and math."),
    ("what are you", "I'm an AI assistant running locally with optional Groq-powered answers when an API key is configured."),
    ("who made you", "I was built as the Starlight AI prototype and improved by the developer working on this project."),
    ("maths", "Sure — send me a math expression or problem, like 'solve 2x+4=10' or 'what is 15% of 80'."),
    ("mathematics", "I can help with arithmetic, equations, percentages, primes, statistics, derivatives, integrals, and unit conversions."),
    ("i don't know", "No worries. Tell me the topic, or pick one: chat, math, planning, explaining, or teaching me a new answer."),
    ("kk", "Got it. What would you like to do next — chat, solve math, or teach me something?"),
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

    def generate_training_answer(self, question, fallback):
        prompt = (
            "Create one high-quality default answer for this local assistant knowledge base. "
            "Keep it under 45 words, specific, and natural. Question: " + question
        )
        return self.chat(prompt) or fallback


def run_training_session(knowledge_engine, provider, progress_callback=None):
    stats = {"topics": 0, "learned": 0, "errors": 0, "provider": "Groq" if provider.enabled else "Local seed"}
    for question, fallback in TRAINING_TOPICS:
        stats["topics"] += 1
        try:
            answer = provider.generate_training_answer(question, fallback)
            existing, conf = knowledge_engine.query_semantic_match(question)
            if existing is None or conf < 0.98:
                knowledge_engine.learn(question, answer)
                stats["learned"] += 1
        except Exception:
            stats["errors"] += 1
        if progress_callback:
            progress_callback(dict(stats))
        time.sleep(0.18)
    return stats
