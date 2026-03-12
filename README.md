# portada-s-index

Biblioteca de algoritmos de similitud para desambiguación de términos históricos.

Diseñada para resolver el problema de normalizar términos ruidosos provenientes de OCR o transcripción manuscrita contra listas de entidades conocidas con sus variantes controladas (voces). Cada término evaluado recibe una clasificación basada en un sistema de votos entre múltiples algoritmos configurables.

---

## Instalación

```bash
# Algoritmos léxicos y fonéticos (instalación base)
pip install portada-s-index

# Con embeddings densos (Tex2Vec / SentenceTransformers)
pip install "portada-s-index[with-embeddings]"

# Con FastText
pip install "portada-s-index[with-fasttext]"

# Con ByT5
pip install "portada-s-index[with-byt5]"

# Todo incluido
pip install "portada-s-index[all]"
```

---

## Uso básico

```python
from portada_s_index import SimilarityService
from portada_s_index.data import VoiceList

# 1. Definir las entidades conocidas con sus variantes
voices = {
    "BERGANTIN": ["bergantín", "bgn", "berg.", "brigantine", "brig", "br"],
    "BOMBARDA":  ["bombarda", "bombarde", "bom", "bomb"],
    "BALANDRA":  ["balandra", "balandro", "bal.", "baland."],
}
voice_list = VoiceList.from_dict("ship_type", voices)

# 2. Configurar los algoritmos
config = {
    "version": 2,
    "normalize": True,
    "consensus": {
        "min_votes": 2,
        "require_levenshtein_ocr": True
    },
    "algorithms": {
        "levenshtein_ocr": {
            "enabled": True,
            "threshold": 0.75,
            "gray_zone": [0.71, 0.749],
            "params": {"confusion_cost": 0.4}
        },
        "jaro_winkler": {
            "enabled": True,
            "threshold": 0.85,
            "gray_zone": [0.80, 0.849],
            "params": {"prefix_weight": 0.1}
        },
        "ngram_2": {
            "enabled": True,
            "threshold": 0.63,
            "gray_zone": [0.60, 0.629],
            "params": {"n": 2}
        },
    }
}

# 3. Crear el servicio
service = SimilarityService.from_dict(config)

# 4. Evaluar términos
terms = [
    {"term": "brig",   "frequency": 34},
    {"term": "bergt",  "frequency": 8},
    {"term": "xyz99",  "frequency": 1},
]

results = service.evaluate(terms, voice_list)
```

La configuración también puede cargarse desde un archivo JSON:

```python
service = SimilarityService.from_file("config.json")
```

---

## Formato de entrada y salida

### Entrada — términos

```python
[
    {"term": "brig",  "frequency": 34},
    {"term": "bergt", "frequency": 8},
]
```

### Entrada — voces

```python
# Desde dict
VoiceList.from_dict("ship_type", {
    "BERGANTIN": ["bergantín", "bgn", "brig"],
    "BOMBARDA":  ["bombarda", "bom"],
})

# Desde archivo .txt con formato jerárquico
VoiceList.from_txt("ship_type", "listas/lista_barcos.txt")
```

Formato del `.txt`:

```
BERGANTIN:
   - bergantín
   - bgn
   - brig
BOMBARDA:
   - bombarda
   - bom
```

### Salida — JSON de resultado por término

```json
{
  "term": "bergt",
  "frequency": 8,
  "normalized": "bergt",
  "exact_match": false,
  "classification": "CONSENSUS",
  "entity": "BERGANTIN",
  "voice": "berg",
  "votes": 3,
  "algorithm_scores": [
    {
      "algorithm": "levenshtein_ocr",
      "best_voice": "berg",
      "best_entity": "BERGANTIN",
      "score": 0.8,
      "threshold": 0.75,
      "voted": true,
      "in_gray_zone": false
    },
    {
      "algorithm": "jaro_winkler",
      "best_voice": "berg",
      "best_entity": "BERGANTIN",
      "score": 0.96,
      "threshold": 0.85,
      "voted": true,
      "in_gray_zone": false
    },
    {
      "algorithm": "ngram_2",
      "best_voice": "berg",
      "best_entity": "BERGANTIN",
      "score": 0.75,
      "threshold": 0.63,
      "voted": true,
      "in_gray_zone": false
    }
  ]
}
```

---

## Clasificaciones

| Clasificación | Condición                                                       |
| ------------- | --------------------------------------------------------------- |
| `EXACT`       | El término normalizado existe directamente como voz conocida    |
| `CONSENSUS`   | ≥ `min_votes` algoritmos votan por la misma entidad             |
| `WEAK`        | ≥ 2 votos por una entidad pero sin cumplir todos los requisitos |
| `ONE_VOTE`    | Solo 1 algoritmo votó a favor                                   |
| `GRAY_ZONE`   | Ningún voto pero al menos 1 algoritmo en zona de incertidumbre  |
| `REJECTED`    | Sin coincidencias significativas                                |

---

## Algoritmos disponibles

| Clave JSON          | Tipo      | Descripción                                         | Dependencia       |
| ------------------- | --------- | --------------------------------------------------- | ----------------- |
| `levenshtein_ocr`   | Léxico    | Levenshtein con costo reducido para confusiones OCR | —                 |
| `levenshtein_ratio` | Léxico    | Levenshtein estándar normalizado                    | —                 |
| `jaro_winkler`      | Léxico    | Jaro-Winkler con peso de prefijo configurable       | —                 |
| `ngram_2`           | Léxico    | Jaccard de bigramas de caracteres                   | —                 |
| `ngram_3`           | Léxico    | Jaccard de trigramas de caracteres                  | —                 |
| `ngram_4`           | Léxico    | Jaccard de cuatrigramas de caracteres               | —                 |
| `phonetic_dm`       | Fonético  | Double Metaphone                                    | `metaphone`       |
| `soundex`           | Fonético  | Soundex clásico                                     | `jellyfish`       |
| `semantica`         | Semántico | Jaccard sobre tokens normalizados                   | —                 |
| `text2vec`          | Semántico | Coseno de vectores TF de n-gramas de caracteres     | —                 |
| `semantic_model`    | Embedding | Embeddings densos (Tex2Vec / SentenceTransformers)  | `with-embeddings` |
| `fasttext`          | Embedding | Embeddings FastText de subpalabras                  | `with-fasttext`   |
| `byt5`              | Embedding | Embeddings ByT5 byte-level                          | `with-byt5`       |

---

## Configuración detallada

Cada algoritmo se configura de forma independiente en el JSON:

```json
{
  "version": 2,
  "normalize": true,
  "consensus": {
    "min_votes": 2,
    "require_levenshtein_ocr": true
  },
  "algorithms": {
    "levenshtein_ocr": {
      "enabled": true,
      "threshold": 0.75,
      "gray_zone": [0.71, 0.749],
      "params": {
        "confusion_cost": 0.4
      }
    },
    "jaro_winkler": {
      "enabled": true,
      "threshold": 0.85,
      "gray_zone": [0.8, 0.849],
      "params": {
        "prefix_weight": 0.1
      }
    },
    "ngram_2": {
      "enabled": true,
      "threshold": 0.63,
      "gray_zone": [0.6, 0.629],
      "params": {
        "n": 2
      }
    },
    "phonetic_dm": {
      "enabled": false,
      "threshold": 0.85,
      "gray_zone": [0.8, 0.849],
      "params": {}
    }
  }
}
```

| Campo                               | Descripción                                                   |
| ----------------------------------- | ------------------------------------------------------------- |
| `normalize`                         | Aplica normalización de texto antes de comparar               |
| `consensus.min_votes`               | Mínimo de algoritmos que deben coincidir en la misma entidad  |
| `consensus.require_levenshtein_ocr` | Si `true`, `levenshtein_ocr` debe estar entre los votantes    |
| `algorithms.*.enabled`              | Activa o desactiva el algoritmo                               |
| `algorithms.*.threshold`            | Score mínimo para que el algoritmo emita un voto              |
| `algorithms.*.gray_zone`            | Rango `[piso, techo]` de incertidumbre, por debajo del umbral |
| `algorithms.*.params`               | Parámetros específicos del algoritmo                          |

---

## Cache de modelos

Los modelos de embeddings se cachean automáticamente:

- **En memoria**: el modelo se carga una sola vez por sesión.
- **En disco**: los embeddings de las voces se guardan en `~/.portada_s_index/cache/` y se reutilizan entre ejecuciones. Si la lista de voces o el modelo cambian, el cache se invalida solo.

```python
from portada_s_index import ModelCache

# Ver modelos en memoria
print(ModelCache.models_in_memory())

# Ver embeddings en disco
print(ModelCache.embeddings_on_disk())

# Limpiar cache
ModelCache.clear_model()
ModelCache.clear_embeddings()
```

---

## Licencia

MIT
