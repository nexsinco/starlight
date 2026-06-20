import re
from difflib import SequenceMatcher
from collections import defaultdict
import random

STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were", "be", "been",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "this", "that", "these", "those", "it", "its", "do", "did", "does",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "they"
}

SYNONYMS = {
    "whats": "what", "sup": "hello", "hi": "hello", "hey": "hello",
    "maker": "creator", "built": "made", "created": "made",
    "yeah": "yes", "nah": "no", "u": "you", "ur": "your", "r": "are",
    "gonna": "going to", "wanna": "want to", "gotta": "got to",
    "dunno": "do not know", "lemme": "let me", "kinda": "kind of",
    "sorta": "sort of", "outta": "out of", "y": "why", "bc": "because",
    "tbh": "to be honest", "imo": "in my opinion", "btw": "by the way",
    "pls": "please", "thx": "thanks", "ty": "thank you", "np": "no problem",
    "ok": "okay", "k": "okay", "nope": "no", "yep": "yes", "yup": "yes",
    "cant": "cannot", "dont": "do not", "doesnt": "does not",
    "isnt": "is not", "wasnt": "was not", "wouldnt": "would not"
}

RESPONSE_TEMPLATES = [
    "Based on what I know, {answer}",
    "Great question! {answer}",
    "Here's what I've learned: {answer}",
    "From my knowledge base: {answer}",
    "{answer}",
    "I think {answer}",
    "My understanding is that {answer}",
]

class MarkovChain:
    """Learns sentence structure to generate coherent new sentences."""
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)
        self.starters = []

    def train(self, text):
        words = text.split()
        if len(words) < self.order + 1:
            return
        self.starters.append(tuple(words[:self.order]))
        for i in range(len(words) - self.order):
            key = tuple(words[i:i + self.order])
            self.model[key].append(words[i + self.order])

    def generate(self, max_words=25, seed=None):
        if not self.starters:
            return ""
        if seed:
            seed_words = seed.split()
            start = None
            for s in self.starters:
                if any(w in seed_words for w in s):
                    start = s
                    break
            if not start:
                start = random.choice(self.starters)
        else:
            start = random.choice(self.starters)

        result = list(start)
        current = start
        for _ in range(max_words - self.order):
            if current not in self.model or not self.model[current]:
                break
            next_word = random.choice(self.model[current])
            result.append(next_word)
            current = tuple(result[-self.order:])

        sentence = " ".join(result)
        if not sentence.endswith((".", "!", "?")):
            sentence += "."
        return sentence.capitalize()


class NLPProcessor:
    markov = MarkovChain(order=2)

    @staticmethod
    def reduce_lengthening(text):
        pattern = re.compile(r"(.)\1{2,}")
        return pattern.sub(r"\1\1", text)  # keep 2, remove 3+

    @staticmethod
    def fix_typo(word, vocabulary):
        if not vocabulary or word in vocabulary:
            return word
        best_match = word
        highest_ratio = 0.0
        for known_word in vocabulary:
            ratio = SequenceMatcher(None, word, known_word).ratio()
            if len(word) >= 2 and word in known_word and len(word) / len(known_word) > 0.5:
                ratio += 0.2
            if ratio > 0.82 and ratio > highest_ratio:
                highest_ratio = ratio
                best_match = known_word
        return best_match

    @staticmethod
    def expand_contractions(text):
        contractions = {
            r"can't": "cannot", r"won't": "will not", r"n't": " not",
            r"'re": " are", r"'ve": " have", r"'ll": " will",
            r"'d": " would", r"'m": " am", r"it's": "it is",
            r"that's": "that is", r"there's": "there is",
        }
        for pattern, replacement in contractions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def process_text(text, vocabulary=None):
        if vocabulary is None:
            vocabulary = set()
        text = NLPProcessor.expand_contractions(text)
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        clean_text = NLPProcessor.reduce_lengthening(clean_text)
        tokens = clean_text.split()
        processed_tokens = []
        for token in tokens:
            token = SYNONYMS.get(token, token)
            if vocabulary:
                token = NLPProcessor.fix_typo(token, vocabulary)
            if token not in STOP_WORDS or len(tokens) <= 3:
                processed_tokens.append(token)
        return processed_tokens

    @staticmethod
    def tokenize_for_vector(text):
        text = NLPProcessor.expand_contractions(text)
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        clean_text = NLPProcessor.reduce_lengthening(clean_text)
        tokens = clean_text.split()
        return [SYNONYMS.get(t, t) for t in tokens]

    @staticmethod
    def tokenize_with_ngrams(text, n=3):
        tokens = NLPProcessor.tokenize_for_vector(text)
        clean = ''.join(tokens)
        ngrams = [clean[i:i + n] for i in range(len(clean) - n + 1)]
        return tokens + ngrams

    @staticmethod
    def wrap_response(answer):
        template = random.choice(RESPONSE_TEMPLATES)
        # Only wrap short factual answers, not full sentences
        if len(answer.split()) <= 10 and not answer[0].isupper():
            return template.format(answer=answer)
        return answer
