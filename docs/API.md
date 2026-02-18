# API Reference - Portada S-Index

## Módulos

- `portada_s_index.algorithms`: Algoritmos de similitud de bajo nivel
- `portada_s_index.similarity`: Clases y funciones principales
- `portada_s_index.utils`: Utilidades de I/O y exportación

## Enumeraciones

### `SimilarityAlgorithm`

Algoritmos de similitud disponibles.

**Valores**:
- `LEVENSHTEIN_OCR`: Levenshtein con corrección OCR
- `LEVENSHTEIN_RATIO`: Levenshtein estándar normalizado
- `JARO_WINKLER`: Jaro-Winkler
- `NGRAM_2`: Similitud de bigramas
- `NGRAM_3`: Similitud de trigramas

**Ejemplo**:
```python
from portada_s_index import SimilarityAlgorithm

algo = SimilarityAlgorithm.LEVENSHTEIN_OCR
print(algo.value)  # "levenshtein_ocr"
```

### `ClassificationLevel`

Niveles de clasificación de nombres.

**Valores**:
- `CONSENSUADO`: Alta confianza (2+ votos misma entidad + Levenshtein OCR)
- `CONSENSUADO_DEBIL`: Confianza moderada (2+ votos pero sin criterio estricto)
- `SOLO_1_VOTO`: Baja confianza (solo 1 algoritmo aprueba)
- `ZONA_GRIS`: Ambiguo (al menos 1 algoritmo en zona gris)
- `RECHAZADO`: Sin correspondencia clara

## Clases

### `SimilarityConfig`

Configuración para cálculo de similitud.

**Constructor**:
```python
SimilarityConfig(
    algorithms: List[SimilarityAlgorithm] = [...],
    thresholds: Dict[SimilarityAlgorithm, float] = {},
    gray_zones: Dict[SimilarityAlgorithm, tuple[float, float]] = {},
    normalize: bool = True,
    min_votes_consensus: int = 2,
    require_levenshtein_ocr: bool = True,
)
```

**Parámetros**:
- `algorithms`: Lista de algoritmos a usar (default: Levenshtein OCR, Jaro-Winkler, NGram 2)
- `thresholds`: Umbrales de aprobación por algoritmo (default: valores predefinidos)
- `gray_zones`: Zonas grises (piso, techo) por algoritmo (default: valores predefinidos)
- `normalize`: Si normalizar texto antes de comparar (default: True)
- `min_votes_consensus`: Votos mínimos para consenso (default: 2)
- `require_levenshtein_ocr`: Si requerir Levenshtein OCR en consenso (default: True)

**Métodos**:

#### `to_dict() -> Dict[str, Any]`
Convierte la configuración a diccionario.

**Returns**: Diccionario con la configuración

**Ejemplo**:
```python
config = SimilarityConfig()
config_dict = config.to_dict()
```

#### `to_json(**kwargs) -> str`
Convierte la configuración a JSON.

**Parameters**: Argumentos para `json.dumps()`

**Returns**: String JSON

**Ejemplo**:
```python
config_json = config.to_json(indent=2)
```

#### `from_dict(data: Dict[str, Any]) -> SimilarityConfig` (classmethod)
Crea configuración desde diccionario.

**Parameters**: Diccionario con configuración

**Returns**: Instancia de SimilarityConfig

#### `from_json(json_str: str) -> SimilarityConfig` (classmethod)
Crea configuración desde JSON.

**Parameters**: String JSON

**Returns**: Instancia de SimilarityConfig

---

### `SimilarityResult`

Resultado de comparación de similitud.

**Atributos**:
- `term` (str): Nombre original
- `voice` (str): Voz comparada
- `algorithm` (SimilarityAlgorithm): Algoritmo usado
- `similarity` (float): Valor de similitud (0.0 a 1.0)
- `approved` (bool): Si supera el umbral de aprobación
- `in_gray_zone` (bool): Si está en zona gris

**Métodos**:

#### `to_dict() -> Dict[str, Any]`
Convierte el resultado a diccionario.

#### `to_json(**kwargs) -> str`
Convierte el resultado a JSON.

---

### `TermClassification`

Clasificación completa de un nombre.

**Atributos**:
- `term` (str): Nombre original
- `frequency` (int): Frecuencia de aparición
- `results` (Dict[SimilarityAlgorithm, SimilarityResult]): Resultados por algoritmo
- `votes_approval` (int): Número de votos de aprobación
- `entity_consensus` (str): Entidad consensuada
- `voice_consensus` (str): Voz consensuada
- `votes_entity` (int): Votos para la entidad consensuada
- `levenshtein_ocr_in_consensus` (bool): Si Levenshtein OCR votó por consenso
- `classification` (ClassificationLevel): Nivel de clasificación

**Métodos**:

#### `to_dict() -> Dict[str, Any]`
Convierte la clasificación a diccionario.

#### `to_json(**kwargs) -> str`
Convierte la clasificación a JSON.

## Funciones principales

### `normalize_text(text: str) -> str`

Normaliza texto a forma canónica.

**Proceso**:
1. Descomposición Unicode (NFD)
2. Eliminación de marcas diacríticas
3. Conversión a minúsculas
4. Eliminación de caracteres no alfabéticos
5. Normalización de espacios

**Parameters**:
- `text`: Texto a normalizar

**Returns**: Texto normalizado

**Ejemplo**:
```python
from portada_s_index import normalize_text

result = normalize_text("Alemán")
print(result)  # "aleman"
```

---

### `calculate_similarity()`

```python
calculate_similarity(
    term: str,
    voices: List[str],
    config: Optional[SimilarityConfig] = None,
    voice_to_entity: Optional[Dict[str, str]] = None,
) -> Dict[SimilarityAlgorithm, SimilarityResult]
```

Calcula similitud de un nombre con lista de voces.

**Parameters**:
- `term`: Nombre a comparar
- `voices`: Lista de voces de referencia
- `config`: Configuración (usa default si None)
- `voice_to_entity`: Mapeo voz normalizada -> entidad (opcional)

**Returns**: Diccionario con resultados por algoritmo

**Ejemplo**:
```python
from portada_s_index import calculate_similarity

results = calculate_similarity(
    term="alemán",
    voices=["aleman", "alemana", "frances"],
)

for algo, result in results.items():
    print(f"{algo.value}: {result.similarity:.4f}")
```

---

### `classify_name()`

```python
classify_name(
    name: List[str],
    voices: List[str],
    frequencies: Optional[Dict[str, int]] = None,
    config: Optional[SimilarityConfig] = None,
    voice_to_entity: Optional[Dict[str, str]] = None,
) -> List[TermClassification]
```

Clasifica lista de nombres según similitud con voces.

**Parameters**:
- `name`: Lista de nombres a clasificar
- `voices`: Lista de voces de referencia
- `frequencies`: Frecuencias por nombre (default: 1 para todos)
- `config`: Configuración (usa default si None)
- `voice_to_entity`: Mapeo voz normalizada -> entidad (opcional)

**Returns**: Lista de clasificaciones

**Ejemplo**:
```python
from portada_s_index import classify_name

classifications = classify_name(
    name=["aleman", "frances"],
    voices=["aleman", "alemana", "frances", "francesa"],
    frequencies={"aleman": 100, "frances": 80},
)

for c in classifications:
    print(f"{c.term}: {c.classification.value}")
```

## Algoritmos de bajo nivel

### `levenshtein_distance(a: str, b: str) -> int`

Calcula distancia de Levenshtein estándar.

**Returns**: Número de operaciones (inserción, eliminación, sustitución)

---

### `levenshtein_ratio(a: str, b: str) -> float`

Calcula similitud de Levenshtein normalizada.

**Returns**: Ratio de similitud (0.0 a 1.0)

---

### `levenshtein_distance_ocr(a: str, b: str, confusion_cost: float = 0.4) -> float`

Calcula distancia de Levenshtein con costos OCR.

**Parameters**:
- `a`, `b`: Cadenas a comparar
- `confusion_cost`: Costo para sustituciones OCR (default: 0.4)

**Returns**: Distancia con costos OCR

---

### `levenshtein_ratio_ocr(a: str, b: str, confusion_cost: float = 0.4) -> float`

Calcula similitud de Levenshtein OCR normalizada.

Para cadenas cortas (≤5 caracteres) usa OCR, para largas usa estándar.

**Returns**: Ratio de similitud con corrección OCR

---

### `jaro_winkler_similarity(a: str, b: str, prefix_weight: float = 0.1) -> float`

Calcula similitud de Jaro-Winkler.

**Parameters**:
- `a`, `b`: Cadenas a comparar
- `prefix_weight`: Peso del prefijo común (default: 0.1)

**Returns**: Similitud Jaro-Winkler (0.0 a 1.0)

---

### `ngram_similarity(a: str, b: str, n: int = 2) -> float`

Calcula similitud basada en n-gramas (Jaccard).

**Parameters**:
- `a`, `b`: Cadenas a comparar
- `n`: Tamaño del n-grama (default: 2)

**Returns**: Similitud de n-gramas (0.0 a 1.0)

## Utilidades

### `load_voices_from_file(file_path: str | Path) -> Tuple[List[str], Dict[str, str]]`

Carga voces desde archivo jerárquico.

**Formato esperado**:
```
ENTIDAD:
  - voz1
  - voz2
```

**Returns**: Tupla con (lista de voces, mapeo voz -> entidad)

**Ejemplo**:
```python
from portada_s_index import load_voices_from_file

voices, voice_to_entity = load_voices_from_file("listas/banderas.txt")
```

---

### `load_name_from_csv(file_path: str | Path) -> Tuple[List[str], Dict[str, int]]`

Carga nombres desde CSV.

**Formato esperado**:
```csv
termino_normalizado,frecuencia,ejemplo_original
termino1,100,Termino1
```

**Returns**: Tupla con (lista de nombres, mapeo nombre -> frecuencia)

---

### `export_classifications_to_json()`

```python
export_classifications_to_json(
    classifications: List[TermClassification],
    output_path: str | Path,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None
```

Exporta clasificaciones a archivo JSON.

---

### `export_classifications_by_level()`

```python
export_classifications_by_level(
    classifications: List[TermClassification],
    output_dir: str | Path,
    prefix: str = "classification",
    indent: int = 2,
) -> Dict[str, Path]
```

Exporta clasificaciones separadas por nivel.

**Returns**: Diccionario con nivel -> ruta del archivo

---

### `generate_summary_report()`

```python
generate_summary_report(
    classifications: List[TermClassification],
    total_occurrences: int,
    config: Optional[SimilarityConfig] = None,
) -> Dict[str, Any]
```

Genera reporte resumen de clasificaciones.

**Returns**: Diccionario con estadísticas

---

### `export_summary_report()`

```python
export_summary_report(
    report: Dict[str, Any],
    output_path: str | Path,
    indent: int = 2,
) -> None
```

Exporta reporte resumen a JSON.

## Constantes

### Umbrales por defecto

```python
DEFAULT_THRESHOLDS = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.75,
    SimilarityAlgorithm.LEVENSHTEIN_RATIO: 0.75,
    SimilarityAlgorithm.JARO_WINKLER: 0.85,
    SimilarityAlgorithm.NGRAM_2: 0.66,
    SimilarityAlgorithm.NGRAM_3: 0.60,
}
```

### Zonas grises por defecto

```python
DEFAULT_GRAY_ZONES = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: (0.71, 0.749),
    SimilarityAlgorithm.LEVENSHTEIN_RATIO: (0.71, 0.749),
    SimilarityAlgorithm.JARO_WINKLER: (0.80, 0.849),
    SimilarityAlgorithm.NGRAM_2: (0.63, 0.659),
    SimilarityAlgorithm.NGRAM_3: (0.55, 0.599),
}
```

### Grupos de confusión OCR

```python
OCR_CONFUSION_GROUPS = [
    {"c", "e"},
    {"p", "n", "r"},
    {"a", "o"},
    {"l", "i", "1"},
    {"m", "n"},
    {"u", "v"},
    {"g", "q"},
    {"h", "b"},
    {"d", "cl"},
    {"rn", "m"},
    {"f", "t"},
    {"s", "5"},
]
```
