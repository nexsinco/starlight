import json
import os
import math
from collections import Counter
from extra_learning_tools import NLPProcessor

FILE = "knowledge.json"

class TFIDFVectorizer:
    """
    Your own sentence transformer – pure math, no external models.
    """
    def __init__(self):
        self.word2id = {}
        self.idf = {}
        self.doc_count = 0
        self.word_doc_counts = Counter()
        self.vocab_size = 0

    def tokenize(self, text):
        # Use the rich tokenizer: words + character n‑grams
        return NLPProcessor.tokenize_with_ngrams(text, n=3)

    def add_document(self, text):
        """Call once for every stored question."""
        tokens = set(self.tokenize(text))
        for token in tokens:
            if token not in self.word2id:
                self.word2id[token] = len(self.word2id)
            self.word_doc_counts[token] += 1
        self.doc_count += 1

    def build_idf(self):
        """Compute IDF after all documents are added."""
        for word, count in self.word_doc_counts.items():
            self.idf[word] = math.log((self.doc_count + 1) / (count + 1)) + 1
        self.vocab_size = len(self.word2id)

    def encode(self, text):
        """Return TF-IDF vector as a list of length vocab_size."""
        if not self.idf:
            self.build_idf()
        tokens = self.tokenize(text)
        tf = Counter(tokens)
        vec = [0.0] * self.vocab_size
        for word, freq in tf.items():
            if word in self.word2id:
                # Sublinear TF scaling
                tf_val = 1 + math.log(freq) if freq > 0 else 0
                vec[self.word2id[word]] = tf_val * self.idf[word]
        return vec

    @staticmethod
    def cosine_sim(v1, v2):
        dot = sum(a*b for a,b in zip(v1, v2))
        norm1 = math.sqrt(sum(a*a for a in v1))
        norm2 = math.sqrt(sum(b*b for b in v2))
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0


class KnowledgeEngine:
    def __init__(self):
        self.vectorizer = TFIDFVectorizer()
        self.questions = []          # stored question strings
        self.answer_by_idx = {}      # index -> answer
        self._load_existing_knowledge()

    def _load_existing_knowledge(self):
        """Load old knowledge.json and convert it to vector store."""
        if not os.path.exists(FILE):
            return
        try:
            with open(FILE, "r") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            raw = {}
        for q_text, data in raw.items():
            answer = data.get("answer") if isinstance(data, dict) else data
            self.learn(q_text, answer, save_to_file=False)

    def learn(self, question, answer, save_to_file=True):
        q = question.strip()
        a = answer.strip()
        self.vectorizer.add_document(q)
        self.vectorizer.build_idf()
        idx = len(self.questions)
        self.questions.append(q)
        self.answer_by_idx[idx] = a
        self._update_all_vectors()
        if save_to_file:
            self._save_to_json(q, a)

    def _update_all_vectors(self):
        self.vectors = [self.vectorizer.encode(q) for q in self.questions]

    def _save_to_json(self, q, a):
        data = {}
        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                data = {}
        data[q] = {"answer": a}
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)

    def query_semantic_match(self, user_question):
        if not self.questions:
            return None, 0.0
        input_vec = self.vectorizer.encode(user_question)
        best_idx = -1
        best_sim = -1.0
        for i, vec in enumerate(self.vectors):
            sim = TFIDFVectorizer.cosine_sim(input_vec, vec)
            if sim > best_sim:
                best_sim = sim
                best_idx = i
        if best_idx != -1:
            return self.answer_by_idx[best_idx], best_sim
        return None, 0.0
