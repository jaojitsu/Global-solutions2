import json
from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np

# Redes neurais (Keras / TensorFlow)
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


"""
Pandora NLU – versão com Rede Neural Recorrente (RNN / LSTM)

- Lê o arquivo intents.json (patterns + tags)
- Treina uma RNN simples (Embedding + LSTM + Dense softmax)
- Salva:
    - Modelo em:   models/pandora_rnn.h5
    - Tokenizer em: models/pandora_tokenizer.pkl
    - Labels em:    models/pandora_labels.json
- Exponde a função predict_intent(text) usada pelo bot Pandora.
"""

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "intents.json"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODELS_DIR / "pandora_rnn.h5"
TOKENIZER_PATH = MODELS_DIR / "pandora_tokenizer.pkl"
LABELS_PATH = MODELS_DIR / "pandora_labels.json"

# hiperparâmetros da rede
MAX_NUM_WORDS = 5000
MAX_SEQUENCE_LENGTH = 20
EMBED_DIM = 64


def load_intents() -> List[dict]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"intents.json não encontrado em {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("intents", [])


def build_dataset(intents: List[dict]):
    """
    Constrói:
    - texts: lista de frases (patterns)
    - labels: índices numéricos das tags
    - tag2idx / idx2tag: mapeamentos entre tag e índice
    """
    texts = []
    tags = []

    for intent in intents:
        tag = intent.get("tag")
        patterns = intent.get("patterns", [])
        for p in patterns:
            if p and isinstance(p, str):
                texts.append(p.strip())
                tags.append(tag)

    if not texts:
        raise ValueError("Nenhuma frase de treino encontrada em intents.json")

    unique_tags = sorted(list(set(tags)))
    tag2idx = {tag: i for i, tag in enumerate(unique_tags)}
    idx2tag = {i: tag for tag, i in tag2idx.items()}

    y = np.array([tag2idx[t] for t in tags], dtype="int32")

    return texts, y, tag2idx, idx2tag


def build_tokenizer(texts: List[str]) -> Tokenizer:
    tokenizer = Tokenizer(num_words=MAX_NUM_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    return tokenizer


def texts_to_padded_sequences(tokenizer: Tokenizer, texts: List[str]):
    seqs = tokenizer.texts_to_sequences(texts)
    return pad_sequences(seqs, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")


def build_model(num_classes: int) -> Sequential:
    model = Sequential(
        [
            Embedding(
                input_dim=MAX_NUM_WORDS,
                output_dim=EMBED_DIM,
                input_length=MAX_SEQUENCE_LENGTH,
            ),
            LSTM(64),
            Dense(32, activation="relu"),
            Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def train_pandora_model(epochs: int = 40, batch_size: int = 8):
    """
    Treina a RNN da Pandora a partir do intents.json e salva o modelo + tokenizer + labels.
    """
    intents = load_intents()
    texts, y, tag2idx, idx2tag = build_dataset(intents)

    tokenizer = build_tokenizer(texts)
    X = texts_to_padded_sequences(tokenizer, texts)

    num_classes = len(tag2idx)
    model = build_model(num_classes)

    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    # salva modelo
    model.save(MODEL_PATH)

    # salva tokenizer
    joblib.dump(tokenizer, TOKENIZER_PATH)

    # salva mapeamento de labels
    labels_info = {
        "tag2idx": tag2idx,
        "idx2tag": {str(k): v for k, v in idx2tag.items()},
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "max_num_words": MAX_NUM_WORDS,
    }
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_info, f, ensure_ascii=False, indent=2)

    print(f"Modelo RNN da Pandora salvo em {MODEL_PATH}")
    print(f"Tokenizer salvo em {TOKENIZER_PATH}")
    print(f"Labels salvos em {LABELS_PATH}")


# ============ PREDIÇÃO (USADO PELO BOT) ============

_MODEL = None
_TOKENIZER = None
_IDX2TAG = None


def _load_artifacts():
    global _MODEL, _TOKENIZER, _IDX2TAG

    if _MODEL is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Modelo RNN da Pandora não encontrado em {MODEL_PATH}. "
                f"Rode train_pandora_model() primeiro."
            )
        _MODEL = load_model(MODEL_PATH)

    if _TOKENIZER is None:
        if not TOKENIZER_PATH.exists():
            raise FileNotFoundError(
                f"Tokenizer da Pandora não encontrado em {TOKENIZER_PATH}. "
                f"Rode train_pandora_model() primeiro."
            )
        _TOKENIZER = joblib.load(TOKENIZER_PATH)

    if _IDX2TAG is None:
        if not LABELS_PATH.exists():
            raise FileNotFoundError(
                f"Arquivo de labels da Pandora não encontrado em {LABELS_PATH}. "
                f"Rode train_pandora_model() primeiro."
            )
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            labels_info = json.load(f)
        _IDX2TAG = {int(k): v for k, v in labels_info["idx2tag"].items()}


def predict_intent(text: str) -> Tuple[str, float]:
    """
    Recebe um texto em linguagem natural e devolve:
        tag  – rótulo previsto (string)
        prob – confiança (float entre 0 e 1)
    """
    _load_artifacts()

    cleaned = (text or "").strip()
    if not cleaned:
        return "fallback", 0.0

    seq = texts_to_padded_sequences(_TOKENIZER, [cleaned])
    probs = _MODEL.predict(seq, verbose=0)[0]
    idx = int(np.argmax(probs))
    prob = float(probs[idx])
    tag = _IDX2TAG.get(idx, "fallback")

    return tag, prob


if __name__ == "__main__":
    print(f"BASE_DIR={BASE_DIR}")
    print(f"DATA_PATH={DATA_PATH} (existe? {DATA_PATH.exists()})")
    train_pandora_model()
