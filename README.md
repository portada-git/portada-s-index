# Portada S-Index

<div align="center">

**Biblioteca Python para desambiguación de nombres históricos mediante algoritmos de similitud de cadenas**

[![PyPI version](https://img.shields.io/pypi/v/portada-s-index.svg)](https://pypi.org/project/portada-s-index/)
[![Python Version](https://img.shields.io/pypi/pyversions/portada-s-index.svg)](https://pypi.org/project/portada-s-index/)
[![License](https://img.shields.io/pypi/l/portada-s-index.svg)](https://github.com/danro-dev/portada-s-index/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/portada-s-index.svg)](https://pypi.org/project/portada-s-index/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintained](https://img.shields.io/badge/maintained-yes-green.svg)](https://github.com/danro-dev/portada-s-index)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/danro-dev/portada-s-index/pulls)

[Características](#características) •
[Instalación](#instalación) •
[Uso Rápido](#uso-rápido) •
[Documentación](#documentación) •
[Ejemplos](#ejemplos)

</div>

---

## 🎯 Descripción

Portada S-Index es una biblioteca especializada en la desambiguación automática de nombres históricos mediante el análisis de similitud con vocabularios controlados. Desarrollada para el proyecto PORTADA, utiliza múltiples algoritmos de similitud de cadenas y un sistema de consenso para clasificar nombres con diferentes niveles de confianza.

**Interfaz principal: JSON** - Todas las entradas y salidas se manejan exclusivamente mediante JSON para máxima interoperabilidad.

## ✨ Características

### 🔧 Algoritmos de Similitud

- **Levenshtein OCR**: Distancia de Levenshtein con corrección para errores comunes de OCR
- **Levenshtein Ratio**: Distancia de Levenshtein estándar normalizada
- **Jaro-Winkler**: Algoritmo optimizado para nombres propios con énfasis en prefijos
- **N-gramas (2 y 3)**: Similitud basada en bigramas y trigramas

### 📊 Sistema de Clasificación

Clasificación automática en 5 niveles de confianza:

| Nivel | Descripción | Criterio |
|-------|-------------|----------|
| **CONSENSUADO** | Alta confianza | 2+ algoritmos votan por la misma entidad + Levenshtein OCR incluido |
| **CONSENSUADO_DEBIL** | Confianza moderada | 2+ algoritmos aprueban sin criterio estricto |
| **SOLO_1_VOTO** | Baja confianza | Solo 1 algoritmo supera el umbral |
| **ZONA_GRIS** | Ambiguo | Al menos 1 algoritmo en zona gris |
| **RECHAZADO** | Sin correspondencia | Ningún algoritmo supera umbrales |

### 🎛️ Configuración Flexible

- Selección de algoritmos a utilizar
- Umbrales de aprobación personalizables por algoritmo
- Zonas grises ajustables para casos ambiguos
- Normalización automática de texto (Unicode, diacríticos, minúsculas)
- Mapeo de voces a entidades para agrupación semántica

### 🚀 Procesamiento Avanzado

- **Procesamiento por lotes**: Múltiples operaciones en una sola llamada
- **Entrada flexible**: Diccionarios Python, strings JSON o archivos JSON
- **Salida estructurada**: Siempre en formato JSON con información completa
- **Reportes estadísticos**: Generación automática de métricas y cobertura

## 📦 Instalación

### Requisitos

- Python >= 3.12
- Sin dependencias externas (solo biblioteca estándar de Python)

### Instalación desde PyPI

```bash
pip install portada-s-index
```

O con uv (más rápido):

```bash
uv pip install portada-s-index
```

### Instalación desde código fuente

```bash
git clone <repository>
cd portada-s-index
pip install -e .
```

O con uv:

```bash
uv pip install -e .
```

## 🚀 Uso Rápido

### Calcular Similitud

```python
from portada_s_index import calculate_similarity_json
import json

# Entrada JSON
input_data = {
    "term": "alemán",
    "voices": ["aleman", "alemana", "germano", "frances"]
}

# Procesar
result_json = calculate_similarity_json(input_data)
result = json.loads(result_json)

# Resultado
print(json.dumps(result, indent=2, ensure_ascii=False))
```

**Salida:**
```json
{
  "term": "alemán",
  "results": {
    "levenshtein_ocr": {
      "voice": "aleman",
      "similarity": 1.0,
      "approved": true
    },
    "jaro_winkler": {
      "voice": "aleman",
      "similarity": 1.0,
      "approved": true
    },
    "ngram_2": {
      "voice": "aleman",
      "similarity": 1.0,
      "approved": true
    }
  }
}
```

### Clasificar Nombres

```python
from portada_s_index import classify_name_json
import json

# Entrada JSON
input_data = {
    "name": ["aleman", "frances", "ingles"],
    "voices": ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa"],
    "frequencies": {
        "aleman": 100,
        "frances": 80,
        "ingles": 150
    }
}

# Procesar
result_json = classify_name_json(input_data)
result = json.loads(result_json)

print(f"Nombres clasificados: {result['total_name']}")
```

### Clasificar con Reporte

```python
from portada_s_index import classify_name_with_report_json
import json

# Entrada JSON (mismo formato que classify_name)
input_data = {
    "name": ["aleman", "frances"],
    "voices": ["aleman", "frances"]
}

# Procesar
result_json = classify_name_with_report_json(input_data)
result = json.loads(result_json)

# Acceder al reporte
report = result["report"]
print(f"Cobertura: {report['coverage']['consensuado_strict']['percentage']:.2f}%")
```

### Procesamiento por Lotes

```python
from portada_s_index import process_batch_json
import json

# Múltiples operaciones en una llamada
input_data = {
    "operations": [
        {
            "type": "calculate_similarity",
            "data": {
                "term": "alemán",
                "voices": ["aleman", "alemana"]
            }
        },
        {
            "type": "classify_name",
            "data": {
                "name": ["frances", "ingles"],
                "voices": ["frances", "ingles"]
            }
        }
    ],
    "config": {
        "algorithms": ["levenshtein_ocr", "jaro_winkler"],
        "normalize": true
    }
}

# Procesar
result_json = process_batch_json(input_data)
result = json.loads(result_json)

print(f"Operaciones exitosas: {result['successful']}/{result['total_operations']}")
```

### Procesar desde Archivos

```python
from portada_s_index import classify_name_from_file

# Procesar archivo JSON y guardar resultado
result_json = classify_name_from_file(
    input_file="input.json",
    output_file="output.json"
)
```

### Orientado a Objetos (Nueva API)

Para implementaciones más estructuradas, puedes usar las clases principales de la librería. Esto facilita la separación de responsabilidades:

```python
from portada_s_index.core import PortAdaSIndex, EntityCitation, KnownEntity
from portada_s_index.similarity import SimilarityConfig

# 1. Configurar
config = SimilarityConfig(algorithms=["levenshtein_ratio", "jaro_winkler"])
index = PortAdaSIndex(config)
index.set_entity_type("Países")

# 2. Cargar Entidades
index.load_known_entities([
    KnownEntity(name="ALEMANIA", voices=["aleman", "alemana", "germano"]),
    KnownEntity(name="FRANCIA", voices=["frances", "francesa"]),
])

# 3. Cargar Citaciones
index.load_citations([
    EntityCitation(id="doc1", cited_name="alemán"),
    EntityCitation(id="doc2", cited_name="frances")
])

# 4. Generar Matriz y Reporte
matrix = index.generate_similarity_matrix()
report = index.get_statistical_report()

print(f"Tipo: {report['entity_type']}")
print(f"Total citaciones analizadas: {report['total_citations']}")
```

## 📖 Documentación

### Estructura de Entrada JSON

#### Entrada Mínima

```json
{
  "name": ["aleman", "frances"],
  "voices": ["aleman", "frances"]
}
```

#### Entrada Completa

```json
{
  "name": ["aleman", "frances"],
  "voices": ["aleman", "alemana", "frances", "francesa"],
  "frequencies": {
    "aleman": 100,
    "frances": 80
  },
  "voice_to_entity": {
    "aleman": "ALEMANIA",
    "alemana": "ALEMANIA",
    "frances": "FRANCIA",
    "francesa": "FRANCIA"
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
}
```

### API Principal

#### Funciones de Entrada JSON

| Función | Descripción |
|---------|-------------|
| `calculate_similarity_json(input_json)` | Calcula similitud de un término con voces |
| `classify_name_json(input_json)` | Clasifica múltiples términos |
| `classify_name_with_report_json(input_json)` | Clasifica términos y genera reporte resumen |
| `process_batch_json(input_json)` | Procesa múltiples operaciones en lote |

#### Funciones de Archivo JSON

| Función | Descripción |
|---------|-------------|
| `calculate_similarity_from_file(input_file, output_file)` | Procesa archivo de similitud |
| `classify_name_from_file(input_file, output_file)` | Procesa archivo de clasificación |
| `classify_name_with_report_from_file(input_file, output_file)` | Procesa con reporte |
| `process_batch_from_file(input_file, output_file)` | Procesa lote desde archivo |

### Algoritmos y Umbrales

| Algoritmo | Identificador | Umbral Default | Zona Gris Default |
|-----------|---------------|----------------|-------------------|
| Levenshtein OCR | `levenshtein_ocr` | 0.75 | [0.71, 0.749] |
| Levenshtein Ratio | `levenshtein_ratio` | 0.75 | [0.71, 0.749] |
| Jaro-Winkler | `jaro_winkler` | 0.85 | [0.80, 0.849] |
| N-gramas 2 | `ngram_2` | 0.66 | [0.63, 0.659] |
| N-gramas 3 | `ngram_3` | 0.60 | [0.55, 0.599] |

## 📚 Documentación Completa

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Arquitectura del paquete y diseño interno
- **[JSON_GUIDE.md](docs/JSON_GUIDE.md)**: Guía completa de formatos JSON con ejemplos
- **[API.md](docs/API.md)**: Referencia detallada de la API
- **[INSTALL.md](docs/INSTALL.md)**: Guía de instalación y configuración
- **[CHANGELOG.md](docs/CHANGELOG.md)**: Historial de cambios

## 💡 Ejemplos

La carpeta `examples/` contiene ejemplos completos de uso (no incluida en el repositorio):

- `json_usage.py`: Ejemplos con JSON en memoria
- `json_file_processing.py`: Procesamiento de archivos JSON
- `input_*.json`: Archivos de ejemplo de entrada
- `quick_test.py`: Tests rápidos sin instalación

### Ejecutar Ejemplos

```bash
# Desde el directorio del proyecto
python3 examples/json_usage.py
python3 examples/json_file_processing.py
```

## 🧪 Testing

### Tests Unitarios

```bash
# Tests básicos
python3 tests/test_basic.py
```

### Test Externo (Simulación Real)

```bash
# Test que simula uso real desde fuera del proyecto
python3 test_portada_external.py
```

**Resultado esperado:**
```
✓ TEST 1: Similitud simple
✓ TEST 2: Clasificación de términos
✓ TEST 3: Clasificación con reporte
✓ TEST 4: Configuración personalizada
✓ TEST 5: Procesamiento por lotes
✓ TEST 6: Mapeo de voces a entidades
✓ TEST 7: Entrada como string JSON

✓ TODOS LOS TESTS EXTERNOS PASARON CORRECTAMENTE
```

### Test con Datos Reales

```bash
# Test con datos reales del proyecto similitudes
python3 test_real_data.py
```

Este test:
1. Convierte CSVs de términos históricos a JSON
2. Carga listas de voces normalizadas
3. Procesa 100 términos reales con los algoritmos
4. Genera reportes estadísticos detallados

**Resultados con datos reales (100 términos, 110,924 ocurrencias):**

| Clasificación | Términos | Ocurrencias | Porcentaje |
|---------------|----------|-------------|------------|
| CONSENSUADO | 92 | 110,567 | 99.68% |
| SOLO_1_VOTO | 7 | 322 | 0.29% |
| RECHAZADO | 1 | 35 | 0.03% |

**Cobertura consensuada: 99.68%** ✨

**Top entidades identificadas:**
- INGLATERRA: 34,976 ocurrencias
- NACIONAL_AR: 14,921 ocurrencias
- FRANCIA: 9,982 ocurrencias
- ITALIA: 9,283 ocurrencias
- ALEMANIA: 6,421 ocurrencias

## 🔧 Configuración Avanzada

### Personalizar Algoritmos

```json
{
  "config": {
    "algorithms": ["levenshtein_ocr", "jaro_winkler"],
    "thresholds": {
      "levenshtein_ocr": 0.80,
      "jaro_winkler": 0.90
    }
  }
}
```

### Ajustar Criterios de Consenso

```json
{
  "config": {
    "min_votes_consensus": 3,
    "require_levenshtein_ocr": false
  }
}
```

### Desactivar Normalización

```json
{
  "config": {
    "normalize": false
  }
}
```

## 🎯 Casos de Uso

### Desambiguación de Banderas de Barcos

```python
input_data = {
    "name": ["aleman", "alemana", "germano"],
    "voices": ["aleman", "alemana", "germano"],
    "voice_to_entity": {
        "aleman": "ALEMANIA",
        "alemana": "ALEMANIA",
        "germano": "ALEMANIA"
    }
}
```

### Normalización de Puertos

```python
input_data = {
    "name": ["barcelona", "barzelona", "barcino"],
    "voices": ["barcelona"],
    "voice_to_entity": {
        "barcelona": "BARCELONA"
    }
}
```

### Clasificación de Tipos de Embarcación

```python
input_data = {
    "name": ["bergantin", "bergantín", "bergatin"],
    "voices": ["bergantin"],
    "frequencies": {
        "bergantin": 150,
        "bergantín": 80,
        "bergatin": 20
    }
}
```

## 📊 Formato de Salida

### Resultado de Similitud

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
    }
  }
}
```

### Clasificación de Nombres

```json
{
  "total_name": 2,
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

### Reporte Resumen

```json
{
  "report": {
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
  },
  "classifications": [...]
}
```

## 🎖️ Resultados con Datos Reales

Pruebas realizadas con datos históricos reales del proyecto PORTADA:

### Dataset de Prueba
- **Fuente**: Banderas de barcos históricos
- **Nombres procesados**: 100
- **Ocurrencias totales**: 110,924
- **Voces de referencia**: 324 (134 entidades)

### Resultados de Clasificación

| Nivel | Nombres | Ocurrencias | Cobertura |
|-------|---------|-------------|-----------|
| **CONSENSUADO** | 92 | 110,567 | **99.68%** |
| SOLO_1_VOTO | 7 | 322 | 0.29% |
| RECHAZADO | 1 | 35 | 0.03% |

### Ejemplos de Clasificación Exitosa

**Nombres con alta frecuencia correctamente identificados:**

| Nombre Original | Frecuencia | Entidad Identificada | Confianza |
|-----------------|------------|---------------------|-----------|
| ingles | 28,247 | INGLATERRA | CONSENSUADO |
| nacional | 14,921 | NACIONAL_AR | CONSENSUADO |
| frances | 6,933 | FRANCIA | CONSENSUADO |
| inglesa | 6,153 | INGLATERRA | CONSENSUADO |
| aleman | 5,154 | ALEMANIA | CONSENSUADO |
| italiano | 4,924 | ITALIA | CONSENSUADO |

### Top 10 Entidades Identificadas

1. **INGLATERRA**: 34,976 ocurrencias
2. **NACIONAL_AR**: 14,921 ocurrencias
3. **FRANCIA**: 9,982 ocurrencias
4. **ITALIA**: 9,283 ocurrencias
5. **ALEMANIA**: 6,421 ocurrencias
6. **URUGUAY**: 5,987 ocurrencias
7. **ESPAÑA**: 5,711 ocurrencias
8. **ESTADOS UNIDOS**: 4,272 ocurrencias
9. **NORUEGA**: 3,717 ocurrencias
10. **ARGENTINA**: 3,241 ocurrencias

### Análisis de Rendimiento

- **Precisión**: 99.68% de las ocurrencias clasificadas con alta confianza
- **Cobertura**: 92% de nombres únicos consensuados
- **Algoritmos**: 91 nombres con 3 votos de aprobación
- **Tiempo de procesamiento**: < 1 segundo para 100 nombres

### Conclusiones

✅ Los algoritmos demuestran **alta precisión** en la identificación de nombres históricos  
✅ El sistema de consenso funciona efectivamente para **reducir falsos positivos**  
✅ La normalización de texto maneja correctamente **variaciones ortográficas**  
✅ El mapeo a entidades permite **agrupación semántica** efectiva

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

[Especificar licencia]

## 👥 Autores

Proyecto PORTADA - Desambiguación de términos históricos marítimos

## 🙏 Agradecimientos

- Proyecto PORTADA
- Comunidad de investigación histórica marítima

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en el repositorio.

---

<div align="center">

**Hecho con ❤️ para el proyecto PORTADA**

</div>
