# Guía de Referencia JSON - Portada S-Index

Esta guía proporciona ejemplos completos de todos los formatos JSON soportados.

## Tabla de contenidos

1. [Calcular similitud](#1-calcular-similitud)
2. [Clasificar términos](#2-clasificar-términos)
3. [Clasificar con reporte](#3-clasificar-con-reporte)
4. [Procesamiento por lotes](#4-procesamiento-por-lotes)
5. [Configuración](#5-configuración)

---

## 1. Calcular similitud

### Entrada mínima

```json
{
  "term": "alemán",
  "voices": ["aleman", "alemana", "frances"]
}
```

### Entrada completa

```json
{
  "term": "alemán",
  "voices": ["aleman", "alemana", "germano", "frances", "ingles"],
  "config": {
    "algorithms": ["levenshtein_ocr", "jaro_winkler", "ngram_2"],
    "thresholds": {
      "levenshtein_ocr": 0.75,
      "jaro_winkler": 0.85,
      "ngram_2": 0.66
    },
    "gray_zones": {
      "levenshtein_ocr": [0.71, 0.749],
      "jaro_winkler": [0.80, 0.849],
      "ngram_2": [0.63, 0.659]
    },
    "normalize": true
  },
  "voice_to_entity": {
    "aleman": "ALEMANIA",
    "alemana": "ALEMANIA",
    "germano": "ALEMANIA"
  }
}
```

### Salida

```json
{
  "term": "alemán",
  "results": {
    "levenshtein_ocr": {
      "term": "alemán",
      "voice": "aleman",
      "algorithm": "levenshtein_ocr",
      "similarity": 1.0,
      "approved": true,
      "in_gray_zone": false
    },
    "jaro_winkler": {
      "term": "alemán",
      "voice": "aleman",
      "algorithm": "jaro_winkler",
      "similarity": 1.0,
      "approved": true,
      "in_gray_zone": false
    },
    "ngram_2": {
      "term": "alemán",
      "voice": "aleman",
      "algorithm": "ngram_2",
      "similarity": 1.0,
      "approved": true,
      "in_gray_zone": false
    }
  }
}
```

---

## 2. Clasificar nombres

### Entrada mínima

```json
{
  "name": ["aleman", "frances"],
  "voices": ["aleman", "frances"]
}
```

### Entrada completa

```json
{
  "name": ["aleman", "frances", "ingles", "italiano", "desconocido"],
  "voices": [
    "aleman", "alemana",
    "frances", "francesa",
    "ingles", "inglesa",
    "italiano", "italiana"
  ],
  "frequencies": {
    "aleman": 100,
    "frances": 80,
    "ingles": 150,
    "italiano": 90,
    "desconocido": 5
  },
  "voice_to_entity": {
    "aleman": "ALEMANIA",
    "alemana": "ALEMANIA",
    "frances": "FRANCIA",
    "francesa": "FRANCIA",
    "ingles": "INGLATERRA",
    "inglesa": "INGLATERRA",
    "italiano": "ITALIA",
    "italiana": "ITALIA"
  },
  "config": {
    "algorithms": ["levenshtein_ocr", "jaro_winkler", "ngram_2"],
    "normalize": true,
    "min_votes_consensus": 2,
    "require_levenshtein_ocr": true
  }
}
```

### Salida

```json
{
  "total_name": 5,
  "classifications": [
    {
      "term": "aleman",
      "frequency": 100,
      "results": {
        "levenshtein_ocr": {
          "similarity": 1.0,
          "voice": "aleman",
          "approved": true,
          "in_gray_zone": false
        },
        "jaro_winkler": {
          "similarity": 1.0,
          "voice": "aleman",
          "approved": true,
          "in_gray_zone": false
        },
        "ngram_2": {
          "similarity": 1.0,
          "voice": "aleman",
          "approved": true,
          "in_gray_zone": false
        }
      },
      "votes_approval": 3,
      "entity_consensus": "ALEMANIA",
      "voice_consensus": "aleman",
      "votes_entity": 3,
      "levenshtein_ocr_in_consensus": true,
      "classification": "CONSENSUADO"
    },
    {
      "term": "desconocido",
      "frequency": 5,
      "results": {
        "levenshtein_ocr": {
          "similarity": 0.45,
          "voice": "italiano",
          "approved": false,
          "in_gray_zone": false
        },
        "jaro_winkler": {
          "similarity": 0.52,
          "voice": "italiano",
          "approved": false,
          "in_gray_zone": false
        },
        "ngram_2": {
          "similarity": 0.30,
          "voice": "italiano",
          "approved": false,
          "in_gray_zone": false
        }
      },
      "votes_approval": 0,
      "entity_consensus": "",
      "voice_consensus": "",
      "votes_entity": 0,
      "levenshtein_ocr_in_consensus": false,
      "classification": "RECHAZADO"
    }
  ]
}
```

---

## 3. Clasificar con reporte

### Entrada

Mismo formato que "Clasificar términos"

### Salida

```json
{
  "report": {
    "total_name": 5,
    "total_occurrences": 425,
    "by_level": {
      "CONSENSUADO": {
        "count": 4,
        "occurrences": 420,
        "percentage": 98.82
      },
      "RECHAZADO": {
        "count": 1,
        "occurrences": 5,
        "percentage": 1.18
      }
    },
    "coverage": {
      "consensuado_strict": {
        "occurrences": 420,
        "percentage": 98.82
      },
      "consensuado_total": {
        "occurrences": 420,
        "percentage": 98.82
      }
    },
    "config": {
      "algorithms": ["levenshtein_ocr", "jaro_winkler", "ngram_2"],
      "thresholds": {
        "levenshtein_ocr": 0.75,
        "jaro_winkler": 0.85,
        "ngram_2": 0.66
      },
      "gray_zones": {
        "levenshtein_ocr": [0.71, 0.749],
        "jaro_winkler": [0.80, 0.849],
        "ngram_2": [0.63, 0.659]
      },
      "normalize": true,
      "min_votes_consensus": 2,
      "require_levenshtein_ocr": true
    }
  },
  "classifications": [
    {
      "term": "aleman",
      "frequency": 100,
      "results": {...},
      "votes_approval": 3,
      "entity_consensus": "ALEMANIA",
      "voice_consensus": "aleman",
      "votes_entity": 3,
      "levenshtein_ocr_in_consensus": true,
      "classification": "CONSENSUADO"
    }
  ]
}
```

---

## 4. Procesamiento por lotes

### Entrada

```json
{
  "operations": [
    {
      "type": "calculate_similarity",
      "data": {
        "term": "alemán",
        "voices": ["aleman", "alemana", "germano"]
      }
    },
    {
      "type": "calculate_similarity",
      "data": {
        "term": "barcelona",
        "voices": ["barcelona", "barzelona", "barcino"]
      }
    },
    {
      "type": "classify_name",
      "data": {
        "name": ["aleman", "frances"],
        "voices": ["aleman", "alemana", "frances", "francesa"],
        "frequencies": {
          "aleman": 100,
          "frances": 80
        }
      }
    },
    {
      "type": "classify_with_report",
      "data": {
        "name": ["italiano", "español"],
        "voices": ["italiano", "italiana", "español", "espanol"],
        "frequencies": {
          "italiano": 90,
          "español": 120
        }
      }
    }
  ],
  "config": {
    "algorithms": ["levenshtein_ocr", "jaro_winkler"],
    "normalize": true
  }
}
```

### Salida

```json
{
  "total_operations": 4,
  "successful": 4,
  "failed": 0,
  "results": [
    {
      "operation_index": 0,
      "type": "calculate_similarity",
      "status": "success",
      "result": {
        "term": "alemán",
        "results": {
          "levenshtein_ocr": {...},
          "jaro_winkler": {...}
        }
      }
    },
    {
      "operation_index": 1,
      "type": "calculate_similarity",
      "status": "success",
      "result": {
        "term": "barcelona",
        "results": {...}
      }
    },
    {
      "operation_index": 2,
      "type": "classify_name",
      "status": "success",
      "result": {
        "total_name": 2,
        "classifications": [...]
      }
    },
    {
      "operation_index": 3,
      "type": "classify_with_report",
      "status": "success",
      "result": {
        "report": {...},
        "classifications": [...]
      }
    }
  ]
}
```

### Salida con error

```json
{
  "total_operations": 2,
  "successful": 1,
  "failed": 1,
  "results": [
    {
      "operation_index": 0,
      "type": "calculate_similarity",
      "status": "success",
      "result": {...}
    },
    {
      "operation_index": 1,
      "type": "unknown_operation",
      "status": "error",
      "error": "Unknown operation type: unknown_operation"
    }
  ]
}
```

---

## 5. Configuración

### Configuración completa

```json
{
  "algorithms": [
    "levenshtein_ocr",
    "levenshtein_ratio",
    "jaro_winkler",
    "ngram_2",
    "ngram_3"
  ],
  "thresholds": {
    "levenshtein_ocr": 0.75,
    "levenshtein_ratio": 0.75,
    "jaro_winkler": 0.85,
    "ngram_2": 0.66,
    "ngram_3": 0.60
  },
  "gray_zones": {
    "levenshtein_ocr": [0.71, 0.749],
    "levenshtein_ratio": [0.71, 0.749],
    "jaro_winkler": [0.80, 0.849],
    "ngram_2": [0.63, 0.659],
    "ngram_3": [0.55, 0.599]
  },
  "normalize": true,
  "min_votes_consensus": 2,
  "require_levenshtein_ocr": true
}
```

### Configuración mínima

```json
{
  "algorithms": ["levenshtein_ocr"]
}
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `algorithms` | array | No | `["levenshtein_ocr", "jaro_winkler", "ngram_2"]` | Algoritmos a usar |
| `thresholds` | object | No | Ver valores por defecto | Umbrales de aprobación |
| `gray_zones` | object | No | Ver valores por defecto | Zonas grises (piso, techo) |
| `normalize` | boolean | No | `true` | Normalizar texto |
| `min_votes_consensus` | integer | No | `2` | Votos mínimos para consenso |
| `require_levenshtein_ocr` | boolean | No | `true` | Requerir Levenshtein OCR en consenso |

---

## Tipos de operación (lotes)

| Tipo | Descripción |
|------|-------------|
| `calculate_similarity` | Calcula similitud de un término |
| `classify_name` | Clasifica múltiples términos |
| `classify_with_report` | Clasifica con reporte resumen |

---

## Algoritmos disponibles

| Algoritmo | Valor | Umbral default | Zona gris default |
|-----------|-------|----------------|-------------------|
| Levenshtein OCR | `levenshtein_ocr` | 0.75 | [0.71, 0.749] |
| Levenshtein Ratio | `levenshtein_ratio` | 0.75 | [0.71, 0.749] |
| Jaro-Winkler | `jaro_winkler` | 0.85 | [0.80, 0.849] |
| N-gramas 2 | `ngram_2` | 0.66 | [0.63, 0.659] |
| N-gramas 3 | `ngram_3` | 0.60 | [0.55, 0.599] |

---

## Niveles de clasificación

| Nivel | Valor | Descripción |
|-------|-------|-------------|
| Consensuado | `CONSENSUADO` | 2+ votos misma entidad + Levenshtein OCR |
| Consensuado débil | `CONSENSUADO_DEBIL` | 2+ votos sin criterio estricto |
| Solo 1 voto | `SOLO_1_VOTO` | Solo 1 algoritmo aprueba |
| Zona gris | `ZONA_GRIS` | Al menos 1 algoritmo en zona gris |
| Rechazado | `RECHAZADO` | Sin correspondencia clara |

---

## Uso desde Python

### Con diccionarios

```python
from portada_s_index import calculate_similarity_json
import json

input_data = {
    "term": "alemán",
    "voices": ["aleman", "alemana"]
}

result_json = calculate_similarity_json(input_data)
result = json.loads(result_json)
```

### Con strings JSON

```python
from portada_s_index import calculate_similarity_json
import json

input_json = '{"term": "alemán", "voices": ["aleman"]}'

result_json = calculate_similarity_json(input_json)
result = json.loads(result_json)
```

### Desde archivos

```python
from portada_s_index import classify_name_from_file

result_json = classify_name_from_file(
    input_file="input.json",
    output_file="output.json"
)
```

---

## Ejemplos completos

Ver carpeta `examples/`:
- `input_similarity.json`: Ejemplo de entrada para similitud
- `input_classification.json`: Ejemplo de entrada para clasificación
- `input_batch.json`: Ejemplo de entrada para lotes
- `json_usage.py`: Ejemplos de uso en Python
- `json_file_processing.py`: Ejemplos con archivos
