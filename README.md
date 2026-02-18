# Portada S-Index

Biblioteca Python para desambiguación de términos históricos mediante algoritmos de similitud de cadenas. Desarrollada para el proyecto PORTADA.

## Características

- **5 algoritmos de similitud**: Levenshtein (estándar y OCR), Jaro-Winkler, N-gramas (2 y 3)
- **Sistema de consenso**: Clasificación automática basada en votación de múltiples algoritmos
- **Configuración flexible**: Umbrales y zonas grises personalizables por algoritmo
- **Salida JSON**: Todos los resultados se exportan en formato JSON estructurado
- **Normalización de texto**: Procesamiento automático de caracteres especiales y diacríticos
- **Utilidades de I/O**: Carga de archivos de voces y términos, exportación de resultados

## Instalación

```bash
pip install portada-s-index
```

## Uso rápido

### Ejemplo básico

```python
from portada_s_index import calculate_similarity

term = "alemán"
voices = ["aleman", "alemana", "germano", "frances"]

results = calculate_similarity(term, voices)

for algo, result in results.items():
    print(f"{algo.value}: {result.voice} ({result.similarity:.4f})")
```

### Clasificación de términos con salida JSON

```python
from portada_s_index import classify_terms
import json

terms = ["aleman", "frances", "ingles"]
voices = ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa"]
frequencies = {"aleman": 100, "frances": 80, "ingles": 150}

classifications = classify_terms(
    terms=terms,
    voices=voices,
    frequencies=frequencies,
)

# Exportar a JSON
output = [c.to_dict() for c in classifications]
print(json.dumps(output, indent=2, ensure_ascii=False))
```

### Configuración personalizada

```python
from portada_s_index import SimilarityConfig, SimilarityAlgorithm

config = SimilarityConfig(
    algorithms=[
        SimilarityAlgorithm.LEVENSHTEIN_OCR,
        SimilarityAlgorithm.JARO_WINKLER,
    ],
    thresholds={
        SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.80,
        SimilarityAlgorithm.JARO_WINKLER: 0.90,
    },
    normalize=True,
)
```

Ver `examples/` para más ejemplos completos.

## Documentación completa

Ver [README completo](https://github.com/danro-dev/portada-s-index) para documentación detallada de API, algoritmos y formatos de archivo.
