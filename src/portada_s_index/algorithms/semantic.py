# ARCHIVO: src/portada_s_index/algorithms/semantic.py
"""
Algoritmos semánticos de similitud.

Implementaciones:
- TokenJaccard  : Jaccard sobre tokens normalizados (sin dependencias)
- CharCosine    : Coseno de vectores TF de n-gramas de caracteres (sin dependencias)
- SemanticModel : Embeddings densos via Tex2Vec o SentenceTransformers
- FastTextModel : Embeddings FastText (word vectors promediados)
- ByT5Model     : Embeddings via modelo ByT5 (byte-level T5)

Las tres últimas tienen dependencias opcionales pesadas.
"""

from __future__ import annotations

import hashlib
import importlib
import os
from pathlib import Path
from typing import Any, ClassVar

import numpy as np

from portada_s_index.algorithms.base import (
    Algorithm,
    AlgorithmNotAvailableError,
    PreprocessedData,
)
from portada_s_index.normalize import normalize_semantic, tokenize_semantic
from portada_s_index.cache import ModelCache


# ---------------------------------------------------------------------------
# Imports opcionales
# ---------------------------------------------------------------------------

try:
    from text2vec import SentenceModel as _Text2VecModel
    _TEXT2VEC_AVAILABLE = True
except ImportError:
    _TEXT2VEC_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer as _STModel
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False

try:
    from transformers import AutoTokenizer as _AutoTokenizer, T5EncoderModel as _T5EncoderModel
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False

try:
    import torch as _torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

try:
    import fasttext as _fasttext
    _FASTTEXT_AVAILABLE = True
except ImportError:
    _FASTTEXT_AVAILABLE = False


# ---------------------------------------------------------------------------
# Algoritmo 9: Token Jaccard
# ---------------------------------------------------------------------------

class TokenJaccard(Algorithm):
    """
    Similitud Jaccard sobre conjuntos de tokens normalizados.

    Jaccard = |tokens(a) ∩ tokens(b)| / |tokens(a) ∪ tokens(b)|

    Usa normalize_semantic(), que elimina artículos, tratamientos
    y diacríticos antes de tokenizar. Rápido y sin dependencias.

    Params:
        mode (str): Solo existe "token_jaccard". Ignorado en runtime,
                    presente en el JSON para documentación.
    """

    name: ClassVar[str] = "token_jaccard"

    def similarity(self, a: str, b: str) -> float:
        tokens_a = set(tokenize_semantic(a))
        tokens_b = set(tokenize_semantic(b))

        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0

        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Algoritmo 10: Char Cosine (TF de n-gramas de caracteres)
# ---------------------------------------------------------------------------

class CharCosine(Algorithm):
    """
    Coseno de vectores TF (term frequency) de n-gramas de caracteres.

    Representa cada string como vector de frecuencias de sus n-gramas
    y calcula la similitud coseno. Captura similitud morfológica
    sin necesitar embeddings entrenados.

    Params:
        mode (str): Solo existe "char_cosine". Presente para documentación.
        n    (int): Tamaño del n-grama. Default 3.
    """

    name: ClassVar[str] = "text2vec"

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        self._n = int(params.get("n", 3))

    def similarity(self, a: str, b: str) -> float:
        na = normalize_semantic(a).replace(" ", "")
        nb = normalize_semantic(b).replace(" ", "")

        vec_a = self._tf_vector(na)
        vec_b = self._tf_vector(nb)

        if not vec_a or not vec_b:
            return 0.0

        # Coseno sobre vocabulario compartido
        keys = set(vec_a) | set(vec_b)
        dot = sum(vec_a.get(k, 0.0) * vec_b.get(k, 0.0) for k in keys)
        norm_a = sum(v ** 2 for v in vec_a.values()) ** 0.5
        norm_b = sum(v ** 2 for v in vec_b.values()) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _tf_vector(self, text: str) -> dict[str, float]:
        n = self._n
        if len(text) < n:
            return {text: 1.0} if text else {}
        ngrams = [text[i: i + n] for i in range(len(text) - n + 1)]
        total = len(ngrams)
        tf: dict[str, float] = {}
        for gram in ngrams:
            tf[gram] = tf.get(gram, 0.0) + 1.0
        return {k: v / total for k, v in tf.items()}


# ---------------------------------------------------------------------------
# Base para algoritmos de embeddings densos
# ---------------------------------------------------------------------------

class _EmbeddingAlgorithm(Algorithm):
    """
    Base para algoritmos que usan embeddings densos.

    Sobreescribe preprocess() para calcular y cachear los embeddings
    de las voces (que no cambian entre ejecuciones con la misma lista).
    Sobreescribe batch() para vectorizar en lote (eficiente).
    """

    def _encode(self, texts: list[str]) -> np.ndarray:
        """Debe ser implementado por subclases."""
        raise NotImplementedError

    def _cache_key_for_voices(self, voices: list[str]) -> str:
        content = "|".join(sorted(voices)) + "|" + self.name
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def preprocess(self, terms: list[str], voices: list[str]) -> PreprocessedData:
        """
        Calcula embeddings de voces y los guarda en cache de disco.
        Los embeddings de términos se calculan en batch() bajo demanda.
        """
        norm_terms = [normalize_semantic(t) for t in terms]
        norm_voices = [normalize_semantic(v) for v in voices]

        cache_key = self._cache_key_for_voices(norm_voices)
        voice_vecs = ModelCache.get_embeddings(
            cache_key=f"{self.name}_{cache_key}",
            compute=lambda: self._encode(norm_voices),
        )

        return PreprocessedData(
            algorithm_name=self.name,
            terms=norm_terms,
            voices=norm_voices,
            extras={
                "voice_vecs": voice_vecs,   # shape: (n_voices, dim)
                "raw_voices": voices,
            },
        )

    def process(self, data: PreprocessedData) -> "SimilarityMatrix":  # noqa: F821
        from portada_s_index.matrix import SimilarityMatrix, Similarity

        self._assert_preprocessed(data)

        voice_vecs: np.ndarray = data.extras["voice_vecs"]
        term_vecs = self._encode(data.terms)  # shape: (n_terms, dim)

        # Similitud coseno en lote: (n_terms, n_voices)
        cosine = np.dot(term_vecs, voice_vecs.T)
        sim_matrix = np.clip((cosine + 1.0) / 2.0, 0.0, 1.0)

        entries = []
        for i, term in enumerate(data.terms):
            for j, voice in enumerate(data.voices):
                entries.append(
                    Similarity(
                        citation_id=term,
                        voice_id=voice,
                        algorithm_name=self.name,
                        similarity_value=round(float(sim_matrix[i, j]), 6),
                    )
                )
        return SimilarityMatrix(algorithm_name=self.name, entries=entries)

    def best_matches(self, data: PreprocessedData) -> dict[str, tuple[str, float]]:
        """
        Calcula solo la mejor voz por término usando batches.

        Evita materializar una matriz completa de todos los términos contra
        todas las voces, que puede ser enorme en entidades como port.
        """
        self._assert_preprocessed(data)

        voice_vecs: np.ndarray = data.extras["voice_vecs"]
        if len(data.voices) == 0:
            return {}

        term_batch_size = int(self.params.get("term_batch_size", 128))
        best_by_term: dict[str, tuple[str, float]] = {}

        for start in range(0, len(data.terms), term_batch_size):
            batch_terms = data.terms[start: start + term_batch_size]
            term_vecs = self._encode(batch_terms)
            cosine = np.dot(term_vecs, voice_vecs.T)
            sim_matrix = np.clip((cosine + 1.0) / 2.0, 0.0, 1.0)
            best_indexes = np.argmax(sim_matrix, axis=1)
            best_scores = sim_matrix[np.arange(len(batch_terms)), best_indexes]

            for term, voice_index, score in zip(batch_terms, best_indexes, best_scores):
                best_by_term[term] = (
                    data.voices[int(voice_index)],
                    round(float(score), 6),
                )

        return best_by_term

    def batch(self, query: str, candidates: list[str]) -> list[float]:
        """Vectoriza query y candidatos en lote para eficiencia."""
        texts = [normalize_semantic(query)] + [normalize_semantic(c) for c in candidates]
        vecs = self._encode(texts)
        query_vec = vecs[0]
        cand_vecs = vecs[1:]
        cosine = np.dot(cand_vecs, query_vec)
        return list(np.clip((cosine + 1.0) / 2.0, 0.0, 1.0).tolist())

    def similarity(self, a: str, b: str) -> float:
        na, nb = normalize_semantic(a), normalize_semantic(b)
        vecs = self._encode([na, nb])
        raw = float(np.dot(vecs[0], vecs[1]))
        return float(np.clip((raw + 1.0) / 2.0, 0.0, 1.0))

    def _normalize_vecs(self, vecs: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.maximum(norms, 1e-10)


# ---------------------------------------------------------------------------
# Algoritmo 11: Semantic Embeddings (Tex2Vec / SentenceTransformers)
# ---------------------------------------------------------------------------

class SemanticModel(_EmbeddingAlgorithm):
    """
    Embeddings densos multilingues via Tex2Vec o SentenceTransformers.

    Elige el backend automáticamente según disponibilidad,
    o el usuario puede especificarlo en params.

    Params:
        backend (str): "text2vec" | "sentence_transformers" | "auto"
        model   (str): Nombre del modelo en HuggingFace Hub.
        device  (str): "cpu" | "cuda". Default "cpu".
    """

    name: ClassVar[str] = "semantic_model"

    _DEFAULT_MODELS = {
        "text2vec": "shibing624/text2vec-base-multilingual",
        "sentence_transformers": "sentence-transformers/LaBSE",
    }

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        backend = params.get("backend", "auto")
        model_name = params.get("model", None)
        device = params.get("device", "cpu")

        if backend == "auto":
            if _TEXT2VEC_AVAILABLE:
                backend = "text2vec"
            elif _ST_AVAILABLE:
                backend = "sentence_transformers"
            else:
                raise AlgorithmNotAvailableError(
                    "semantic_model requiere 'text2vec' o 'sentence-transformers'.\n"
                    "Instala con: pip install text2vec\n"
                    "o: pip install sentence-transformers"
                )

        self._backend = backend
        resolved_model = model_name or self._DEFAULT_MODELS[backend]
        cache_key = f"{self.name}_{backend}_{resolved_model}"

        if backend == "text2vec":
            if not _TEXT2VEC_AVAILABLE:
                raise AlgorithmNotAvailableError(
                    "text2vec no está instalado.\npip install text2vec"
                )
            self._model = ModelCache.get_model(
                cache_key,
                lambda: _Text2VecModel(resolved_model),
            )
        else:
            if not _ST_AVAILABLE:
                raise AlgorithmNotAvailableError(
                    "sentence-transformers no está instalado.\n"
                    "pip install sentence-transformers"
                )
            self._model = ModelCache.get_model(
                cache_key,
                lambda: _STModel(resolved_model, device=device),
            )

    def _encode(self, texts: list[str]) -> np.ndarray:
        if self._backend == "text2vec":
            vecs = self._model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        else:
            vecs = self._model.encode(
                texts,
                batch_size=256,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        return self._normalize_vecs(np.array(vecs, dtype=np.float32))


class SemanticText2Vec(SemanticModel):
    """SemanticModel alias fixed to the text2vec backend."""

    name: ClassVar[str] = "semantic_text2vec"

    def __init__(self, params: dict[str, Any]) -> None:
        params = {
            "backend": "text2vec",
            "model": "shibing624/text2vec-base-multilingual",
            **params,
        }
        super().__init__(params)


class SentenceTransformerLABSE(SemanticModel):
    """SemanticModel alias fixed to the LaBSE sentence-transformers model."""

    name: ClassVar[str] = "sentence_transformer_labse"

    def __init__(self, params: dict[str, Any]) -> None:
        params = {
            "backend": "sentence_transformers",
            "model": "sentence-transformers/LaBSE",
            **params,
        }
        super().__init__(params)


class SentenceTransformerMPNet(SemanticModel):
    """SemanticModel alias fixed to the multilingual MPNet sentence-transformers model."""

    name: ClassVar[str] = "sentence_transformer_mpnet"

    def __init__(self, params: dict[str, Any]) -> None:
        params = {
            "backend": "sentence_transformers",
            "model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            **params,
        }
        super().__init__(params)


# ---------------------------------------------------------------------------
# Algoritmo 12: FastText
# ---------------------------------------------------------------------------

class FastTextModel(_EmbeddingAlgorithm):
    """
    Embeddings FastText (vectores de subpalabras promediados).

    Especialmente robusto ante errores ortográficos y palabras
    fuera de vocabulario, ya que opera a nivel de n-gramas de caracteres.

    Requiere: `pip install fasttext` y un modelo .bin descargado.

    Params:
        model_path (str): Ruta al archivo .bin del modelo FastText.
    """

    name: ClassVar[str] = "fasttext"

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        if not _FASTTEXT_AVAILABLE:
            raise AlgorithmNotAvailableError(
                "fasttext no está instalado.\npip install fasttext"
            )
        model_path = params.get("model_path")
        if not model_path:
            raise ValueError(
                "fasttext requiere 'model_path' en params: "
                "ruta al archivo .bin del modelo."
            )
        path = self._ensure_model_path(params)
        self._model_path = path
        self._model = ModelCache.get_model(
            f"fasttext_{path}",
            lambda: _fasttext.load_model(str(path)),
        )

    def _ensure_model_path(self, params: dict[str, Any]) -> Path:
        model_path = params.get("model_path")
        path = Path(model_path)
        if not path.exists():
            if params.get("auto_download", False):
                return self._download_model(params, path)
            raise FileNotFoundError(
                f"Modelo FastText no encontrado: {path}\n"
                f"Descarga el modelo desde https://fasttext.cc/docs/en/crawl-vectors.html"
            )
        return path

    def _download_model(self, params: dict[str, Any], requested_path: Path) -> Path:
        """Descarga explícita del modelo FastText si params.auto_download=True."""
        lang = str(params.get("lang", "es"))
        cache_dir = Path(params.get("cache_dir") or requested_path.parent)
        cache_dir.mkdir(parents=True, exist_ok=True)

        fasttext_util = importlib.import_module("fasttext.util")
        previous_cwd = Path.cwd()
        try:
            os.chdir(cache_dir)
            fasttext_util.download_model(lang, if_exists="ignore")
        finally:
            os.chdir(previous_cwd)

        downloaded_path = cache_dir / f"cc.{lang}.300.bin"
        if requested_path.exists():
            return requested_path
        if downloaded_path.exists():
            return downloaded_path
        raise FileNotFoundError(
            f"FastText auto_download no generó el modelo esperado: {requested_path}"
        )

    def _encode(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(
            [self._model.get_sentence_vector(t) for t in texts],
            dtype=np.float32,
        )
        return self._normalize_vecs(vecs)


# ---------------------------------------------------------------------------
# Algoritmo 12b: ByT5
# ---------------------------------------------------------------------------

class ByT5Model(_EmbeddingAlgorithm):
    """
    Embeddings via modelo ByT5 (byte-level T5).

    Opera directamente sobre bytes, sin tokenizador de subpalabras.
    Muy robusto ante ruido ortográfico extremo y lenguas poco
    representadas en otros modelos.

    Requiere: `pip install transformers torch`.

    Params:
        model   (str): Nombre del modelo encoder en HuggingFace Hub.
                       Default "agusnieto77/byt5-portada-contrastivo".
        device  (str): "cpu" | "cuda". Default "cpu".
        max_length (int): Longitud máxima de tokenización. Default 128.
    """

    name: ClassVar[str] = "byt5"

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        if not _TRANSFORMERS_AVAILABLE:
            raise AlgorithmNotAvailableError(
                "byt5 requiere 'transformers'.\npip install transformers"
            )
        if not _TORCH_AVAILABLE:
            raise AlgorithmNotAvailableError(
                "byt5 requiere 'torch'.\npip install torch"
            )
        model_name = params.get("model", "agusnieto77/byt5-portada-contrastivo")
        self._device = params.get("device", "cpu")
        self._max_length = int(params.get("max_length", 128))
        self._torch_dtype = self._resolve_torch_dtype(params.get("torch_dtype", "float32"))

        self._tokenizer, self._model_nn = ModelCache.get_model(
            f"byt5_{model_name}_{self._device}_{params.get('torch_dtype', 'float32')}_{self._max_length}",
            lambda: self._load(model_name),
        )

    def _resolve_torch_dtype(self, dtype_name: str):
        dtype_name = str(dtype_name).lower()
        if dtype_name in {"float32", "fp32"}:
            return _torch.float32
        if dtype_name in {"float16", "fp16"}:
            return _torch.float16
        if dtype_name in {"bfloat16", "bf16"}:
            return _torch.bfloat16
        if dtype_name == "auto":
            return "auto"
        raise ValueError(
            "byt5 params.torch_dtype debe ser 'float32', 'float16', 'bfloat16' o 'auto'"
        )

    def _load(self, model_name: str):
        tokenizer = _AutoTokenizer.from_pretrained(model_name)
        model = _T5EncoderModel.from_pretrained(
            model_name,
            torch_dtype=self._torch_dtype,
        ).to(self._device)
        model.eval()
        return tokenizer, model

    def _encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        all_vecs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i + batch_size]
            inputs = self._tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self._max_length,
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            with _torch.no_grad():
                outputs = self._model_nn(**inputs)
            mask = (
                inputs["attention_mask"]
                .unsqueeze(-1)
                .expand(outputs.last_hidden_state.size())
                .float()
            )
            vecs = (
                (outputs.last_hidden_state.float() * mask).sum(1)
                / mask.sum(1).clamp(min=1e-9)
            ).cpu().numpy()
            all_vecs.append(vecs)
        result = np.concatenate(all_vecs, axis=0).astype(np.float32)
        return self._normalize_vecs(result)
