# Guía de Instalación y Uso - Portada S-Index

## Instalación

### Opción 1: Instalación desde el código fuente (Desarrollo)

```bash
# Clonar o navegar al directorio del proyecto
cd portada-s-index

# Instalar en modo desarrollo
pip install -e .
```

### Opción 2: Instalación con uv (Recomendado)

```bash
# Si tienes uv instalado
uv pip install -e .
```

### Opción 3: Uso sin instalación

Puedes usar la biblioteca sin instalarla agregando el directorio `src` al path de Python:

```python
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Ahora puedes importar
from portada_s_index import calculate_similarity
```

## Verificar la instalación

### Ejecutar tests rápidos

```bash
cd portada-s-index
python3 examples/quick_test.py
```

Deberías ver una salida similar a:

```
╔════════════════════════════════════════════════════════════════════╗
║               PORTADA S-INDEX - TESTS RÁPIDOS                     ║
╚════════════════════════════════════════════════════════════════════╝

======================================================================
TEST 1: Normalización de texto
======================================================================
✓ 'Alemán' -> 'aleman' (esperado: 'aleman')
...
======================================================================
✓ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE
======================================================================
```

## Uso básico

### 1. Calcular similitud simple

```python
from portada_s_index import calculate_similarity
import json

term = "alemán"
voices = ["aleman", "alemana", "germano", "frances"]

results = calculate_similarity(term, voices)

# Ver resultados
for algo, result in results.items():
    print(f"{algo.value}: {result.voice} ({result.similarity:.4f})")

# Exportar a JSON
result_json = results[list(results.keys())[0]].to_json()
print(result_json)
```

### 2. Clasificar términos

```python
from portada_s_index import classify_name
import json

name = ["aleman", "frances", "ingles"]
voices = ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa"]
frequencies = {"aleman": 100, "frances": 80, "ingles": 150}

classifications = classify_name(
    name=name,
    voices=voices,
    frequencies=frequencies,
)

# Exportar a JSON
output = [c.to_dict() for c in classifications]
print(json.dumps(output, indent=2, ensure_ascii=False))
```

### 3. Configuración personalizada

```python
from portada_s_index import SimilarityConfig, SimilarityAlgorithm, calculate_similarity

# Crear configuración
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

# Usar configuración
results = calculate_similarity("barcelona", ["barcelona", "barzelona"], config)

# Exportar configuración a JSON
config_json = config.to_json(indent=2)
print(config_json)
```

### 4. Procesar archivos

```python
from portada_s_index import (
    load_voices_from_file,
    load_name_from_csv,
    classify_name,
    export_classifications_to_json,
    generate_summary_report,
    export_summary_report,
)

# Cargar datos
voices, voice_to_entity = load_voices_from_file("listas/lista_banderas.txt")
name, frequencies = load_name_from_csv("datos/terminos_ship_flag.csv")

# Clasificar
classifications = classify_name(
    name=name,
    voices=voices,
    frequencies=frequencies,
    voice_to_entity=voice_to_entity,
)

# Exportar resultados completos
export_classifications_to_json(
    classifications,
    "output/results.json",
    indent=2,
)

# Generar y exportar reporte resumen
total_occurrences = sum(frequencies.values())
report = generate_summary_report(classifications, total_occurrences)
export_summary_report(report, "output/report.json")

print(f"Procesados {len(classifications)} términos")
print(f"Cobertura consensuada: {report['coverage']['consensuado_strict']['percentage']:.2f}%")
```

## Ejemplos completos

El directorio `examples/` contiene ejemplos completos:

### Ejecutar ejemplo básico

```bash
cd portada-s-index
python3 examples/basic_usage.py
```

### Ejecutar ejemplo de procesamiento de archivos

```bash
cd portada-s-index
python3 examples/file_processing.py
```

## Estructura de salida JSON

### Resultado de similitud

```json
{
  "term": "alemán",
  "voice": "aleman",
  "algorithm": "levenshtein_ocr",
  "similarity": 0.95,
  "approved": true,
  "in_gray_zone": false
}
```

### Clasificación de término

```json
{
  "term": "aleman",
  "frequency": 100,
  "results": {
    "levenshtein_ocr": {
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
}
```

### Reporte resumen

```json
{
  "total_name": 100,
  "total_occurrences": 5000,
  "by_level": {
    "CONSENSUADO": {
      "count": 75,
      "occurrences": 4500,
      "percentage": 90.0
    }
  },
  "coverage": {
    "consensuado_strict": {
      "occurrences": 4500,
      "percentage": 90.0
    }
  }
}
```

## Algoritmos disponibles

- `SimilarityAlgorithm.LEVENSHTEIN_OCR`: Levenshtein con corrección OCR
- `SimilarityAlgorithm.LEVENSHTEIN_RATIO`: Levenshtein estándar
- `SimilarityAlgorithm.JARO_WINKLER`: Jaro-Winkler
- `SimilarityAlgorithm.NGRAM_2`: Bigramas
- `SimilarityAlgorithm.NGRAM_3`: Trigramas

## Niveles de clasificación

- `ClassificationLevel.CONSENSUADO`: Alta confianza
- `ClassificationLevel.CONSENSUADO_DEBIL`: Confianza moderada
- `ClassificationLevel.SOLO_1_VOTO`: Baja confianza
- `ClassificationLevel.ZONA_GRIS`: Ambiguo
- `ClassificationLevel.RECHAZADO`: Sin correspondencia

## Solución de problemas

### ModuleNotFoundError: No module named 'portada_s_index'

Asegúrate de haber instalado el paquete o de agregar el directorio `src` al path:

```python
import sys
sys.path.insert(0, "src")
```

### Errores de encoding en archivos

Asegúrate de que tus archivos estén en UTF-8:

```python
# Al leer archivos manualmente
with open("archivo.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

## Soporte

Para más información, consulta:
- README.md: Documentación completa
- examples/: Ejemplos de uso
- tests/: Tests unitarios

## Requisitos

- Python >= 3.12
- No requiere dependencias externas (solo biblioteca estándar)
