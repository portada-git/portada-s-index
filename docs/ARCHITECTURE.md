# Arquitectura de Portada S-Index

## Visión General

Portada S-Index es una biblioteca Python diseñada con una arquitectura modular de tres capas que separa claramente las responsabilidades: algoritmos de bajo nivel, lógica de negocio y interfaz de usuario.

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ JSON                            │
│              (json_interface.py)                            │
│  • Entrada/Salida exclusivamente JSON                       │
│  • Procesamiento por lotes                                  │
│  • Manejo de archivos                                       │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  LÓGICA DE NEGOCIO                          │
│               (similarity.py)                               │
│  • Clases de configuración y resultados                     │
│  • Sistema de clasificación por consenso                    │
│  • Orquestación de algoritmos                               │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ALGORITMOS DE SIMILITUD                        │
│               (algorithms.py)                               │
│  • Levenshtein (estándar y OCR)                            │
│  • Jaro-Winkler                                            │
│  • N-gramas (2 y 3)                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    UTILIDADES                               │
│                  (utils.py)                                 │
│  • Carga de datos (CSV, listas jerárquicas)               │
│  • Exportación de resultados                                │
│  • Generación de reportes                                   │
└─────────────────────────────────────────────────────────────┘
```

## Arquitectura en Capas

```
┌──────────────────────────────────────────────────────────────┐
│                         USUARIO                              │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ JSON
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    CAPA DE INTERFAZ                          │
│                                                              │
│  calculate_similarity_json()                                 │
│  classify_name_json()                                       │
│  classify_name_with_report_json()                          │
│  process_batch_json()                                        │
│                                                              │
│  Responsabilidad:                                            │
│  • Parseo y validación de JSON                              │
│  • Serialización de resultados                              │
│  • Manejo de errores                                        │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Python Objects
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  CAPA DE LÓGICA DE NEGOCIO                   │
│                                                              │
│  calculate_similarity()                                      │
│  classify_name()                                            │
│  normalize_text()                                            │
│                                                              │
│  Clases:                                                     │
│  • SimilarityConfig                                         │
│  • SimilarityResult                                         │
│  • TermClassification                                       │
│                                                              │
│  Responsabilidad:                                            │
│  • Orquestación de algoritmos                               │
│  • Sistema de votación y consenso                           │
│  • Clasificación por niveles de confianza                   │
│  • Normalización de texto                                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Normalized Strings
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   CAPA DE ALGORITMOS                         │
│                                                              │
│  levenshtein_ratio_ocr()                                     │
│  jaro_winkler_similarity()                                   │
│  ngram_similarity()                                          │
│                                                              │
│  Responsabilidad:                                            │
│  • Cálculo puro de similitud                                │
│  • Sin estado ni efectos secundarios                        │
│  • Optimización de rendimiento                              │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Similarity Scores
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      CAPA DE UTILIDADES                      │
│                                                              │
│  load_voices_from_file()                                     │
│  load_name_from_csv()                                       │
│  export_classifications_to_json()                           │
│  generate_summary_report()                                   │
│                                                              │
│  Responsabilidad:                                            │
│  • I/O de archivos                                          │
│  • Generación de reportes                                   │
│  • Exportación de resultados                                │
└──────────────────────────────────────────────────────────────┘
```

## Estructura de Módulos

### 1. `algorithms.py` - Capa de Algoritmos

**Responsabilidad**: Implementación pura de algoritmos de similitud de cadenas.

**Características**:
- Sin dependencias externas (solo biblioteca estándar)
- Funciones puras sin estado
- Optimizadas para rendimiento
- Independientes del dominio de aplicación

**Algoritmos Implementados**:

```python
# Levenshtein estándar
levenshtein_distance(a: str, b: str) -> int
levenshtein_ratio(a: str, b: str) -> float

# Levenshtein con corrección OCR
levenshtein_distance_ocr(a: str, b: str, confusion_cost: float) -> float
levenshtein_ratio_ocr(a: str, b: str, confusion_cost: float) -> float

# Jaro-Winkler
jaro_winkler_similarity(a: str, b: str, prefix_weight: float) -> float

# N-gramas
ngram_similarity(a: str, b: str, n: int) -> float
```

**Grupos de Confusión OCR**:
```python
OCR_CONFUSION_GROUPS = [
    {"c", "e"},      # Confusión común en OCR
    {"p", "n", "r"}, # Caracteres similares
    {"a", "o"},      # Vocales redondeadas
    {"l", "i", "1"}, # Líneas verticales
    # ... más grupos
]
```

**Diseño**:
- Cada algoritmo es una función independiente
- Retornan valores normalizados (0.0 a 1.0)
- No tienen efectos secundarios
- Fácilmente testeable

---

### 2. `similarity.py` - Capa de Lógica de Negocio

**Responsabilidad**: Orquestación de algoritmos, clasificación y lógica de consenso.

#### 2.1 Enumeraciones

```python
class SimilarityAlgorithm(Enum):
    """Identificadores de algoritmos disponibles."""
    LEVENSHTEIN_OCR = "levenshtein_ocr"
    LEVENSHTEIN_RATIO = "levenshtein_ratio"
    JARO_WINKLER = "jaro_winkler"
    NGRAM_2 = "ngram_2"
    NGRAM_3 = "ngram_3"

class ClassificationLevel(Enum):
    """Niveles de confianza en la clasificación."""
    CONSENSUADO = "CONSENSUADO"           # Alta confianza
    CONSENSUADO_DEBIL = "CONSENSUADO_DEBIL"  # Confianza moderada
    SOLO_1_VOTO = "SOLO_1_VOTO"          # Baja confianza
    ZONA_GRIS = "ZONA_GRIS"              # Ambiguo
    RECHAZADO = "RECHAZADO"              # Sin correspondencia
```

#### 2.2 Clases de Configuración

```python
@dataclass
class SimilarityConfig:
    """Configuración flexible para el sistema."""
    algorithms: List[SimilarityAlgorithm]
    thresholds: Dict[SimilarityAlgorithm, float]
    gray_zones: Dict[SimilarityAlgorithm, Tuple[float, float]]
    normalize: bool
    min_votes_consensus: int
    require_levenshtein_ocr: bool
    
    # Métodos de serialización
    def to_dict() -> Dict
    def to_json() -> str
    @classmethod
    def from_dict(data: Dict) -> SimilarityConfig
    @classmethod
    def from_json(json_str: str) -> SimilarityConfig
```

**Valores por Defecto**:
```python
DEFAULT_ALGORITHMS = [
    SimilarityAlgorithm.LEVENSHTEIN_OCR,
    SimilarityAlgorithm.JARO_WINKLER,
    SimilarityAlgorithm.NGRAM_2,
]

DEFAULT_THRESHOLDS = {
    LEVENSHTEIN_OCR: 0.75,
    LEVENSHTEIN_RATIO: 0.75,
    JARO_WINKLER: 0.85,
    NGRAM_2: 0.66,
    NGRAM_3: 0.60,
}

DEFAULT_GRAY_ZONES = {
    LEVENSHTEIN_OCR: (0.71, 0.749),
    JARO_WINKLER: (0.80, 0.849),
    # ...
}
```

#### 2.3 Clases de Resultados

```python
@dataclass
class SimilarityResult:
    """Resultado de un algoritmo individual."""
    term: str                          # Nombre original
    voice: str                         # Voz comparada
    algorithm: SimilarityAlgorithm     # Algoritmo usado
    similarity: float                  # Valor de similitud
    approved: bool                     # Supera umbral
    in_gray_zone: bool                 # Está en zona gris
    
    def to_dict() -> Dict
    def to_json() -> str

@dataclass
class TermClassification:
    """Clasificación completa de un nombre."""
    term: str                          # Nombre original
    frequency: int                     # Frecuencia de aparición
    results: Dict[SimilarityAlgorithm, SimilarityResult]
    votes_approval: int                # Votos de aprobación
    entity_consensus: str              # Entidad consensuada
    voice_consensus: str               # Voz consensuada
    votes_entity: int                  # Votos para entidad
    levenshtein_ocr_in_consensus: bool # Levenshtein OCR votó
    classification: ClassificationLevel # Nivel de clasificación
    
    def to_dict() -> Dict
    def to_json() -> str
```

#### 2.4 Funciones Principales

```python
def normalize_text(text: str) -> str:
    """
    Normalización de texto a forma canónica.
    
    Proceso:
    1. Descomposición Unicode (NFD)
    2. Eliminación de diacríticos
    3. Conversión a minúsculas
    4. Eliminación de no-alfabéticos
    5. Normalización de espacios
    """

def calculate_similarity(
    term: str,
    voices: List[str],
    config: Optional[SimilarityConfig],
    voice_to_entity: Optional[Dict[str, str]],
) -> Dict[SimilarityAlgorithm, SimilarityResult]:
    """
    Calcula similitud de un nombre con lista de voces.
    
    Flujo:
    1. Normalizar nombre si config.normalize
    2. Para cada algoritmo configurado:
       a. Calcular similitud con cada voz
       b. Seleccionar mejor coincidencia
       c. Evaluar contra umbral y zona gris
    3. Retornar resultados por algoritmo
    """

def classify_name(
    name: List[str],
    voices: List[str],
    frequencies: Optional[Dict[str, int]],
    config: Optional[SimilarityConfig],
    voice_to_entity: Optional[Dict[str, str]],
) -> List[TermClassification]:
    """
    Clasifica lista de nombres según similitud.
    
    Flujo:
    1. Para cada nombre:
       a. Calcular similitud con todas las voces
       b. Contar votos de aprobación
       c. Determinar consenso de entidad
       d. Aplicar reglas de clasificación
    2. Retornar lista de clasificaciones
    """
```

#### 2.5 Sistema de Clasificación

**Reglas de Clasificación**:

```python
def _classify_term(
    votes_approval: int,
    votes_entity: int,
    has_gray_zone: bool,
    levenshtein_ocr_approved: bool,
    config: SimilarityConfig,
) -> ClassificationLevel:
    """
    Lógica de clasificación por consenso.
    
    Reglas:
    1. CONSENSUADO:
       - votes_entity >= min_votes_consensus
       - levenshtein_ocr_approved (si require_levenshtein_ocr)
    
    2. CONSENSUADO_DEBIL:
       - votes_approval >= min_votes_consensus
       - No cumple criterio estricto
    
    3. ZONA_GRIS:
       - Al menos 1 algoritmo en zona gris
    
    4. SOLO_1_VOTO:
       - votes_approval == 1
    
    5. RECHAZADO:
       - votes_approval == 0
    """
```

---

### 3. `json_interface.py` - Capa de Interfaz

**Responsabilidad**: Interfaz JSON para entrada/salida y procesamiento por lotes.

#### 3.1 Funciones de Entrada JSON

```python
def calculate_similarity_json(
    input_json: str | Dict[str, Any]
) -> str:
    """
    Calcula similitud desde JSON.
    
    Entrada:
    {
        "term": "alemán",
        "voices": ["aleman", "alemana"],
        "config": {...},  // opcional
        "voice_to_entity": {...}  // opcional
    }
    
    Salida:
    {
        "term": "alemán",
        "results": {
            "levenshtein_ocr": {...},
            "jaro_winkler": {...}
        }
    }
    """

def classify_name_json(
    input_json: str | Dict[str, Any]
) -> str:
    """
    Clasifica nombres desde JSON.
    
    Entrada:
    {
        "name": ["aleman", "frances"],
        "voices": ["aleman", "frances"],
        "frequencies": {...},  // opcional
        "config": {...},  // opcional
        "voice_to_entity": {...}  // opcional
    }
    
    Salida:
    {
        "total_name": 2,
        "classifications": [...]
    }
    """

def classify_name_with_report_json(
    input_json: str | Dict[str, Any]
) -> str:
    """
    Clasifica con reporte resumen.
    
    Salida:
    {
        "report": {
            "total_name": 2,
            "total_occurrences": 180,
            "by_level": {...},
            "coverage": {...}
        },
        "classifications": [...]
    }
    """
```

#### 3.2 Procesamiento por Lotes

```python
def process_batch_json(
    input_json: str | Dict[str, Any]
) -> str:
    """
    Procesa múltiples operaciones en lote.
    
    Entrada:
    {
        "operations": [
            {
                "type": "calculate_similarity",
                "data": {...}
            },
            {
                "type": "classify_name",
                "data": {...}
            }
        ],
        "config": {...}  // configuración global opcional
    }
    
    Salida:
    {
        "total_operations": 2,
        "successful": 2,
        "failed": 0,
        "results": [
            {
                "operation_index": 0,
                "type": "calculate_similarity",
                "status": "success",
                "result": {...}
            }
        ]
    }
    """
```

#### 3.3 Funciones de Archivo

```python
def calculate_similarity_from_file(
    input_file: str | Path,
    output_file: Optional[str | Path]
) -> str:
    """Lee JSON de archivo, procesa y opcionalmente guarda."""

def classify_name_from_file(...) -> str:
    """Clasifica desde archivo JSON."""

def classify_name_with_report_from_file(...) -> str:
    """Clasifica con reporte desde archivo."""

def process_batch_from_file(...) -> str:
    """Procesa lote desde archivo."""
```

---

### 4. `utils.py` - Capa de Utilidades

**Responsabilidad**: Funciones auxiliares para I/O y reportes.

#### 4.1 Carga de Datos

```python
def load_voices_from_file(
    file_path: str | Path
) -> Tuple[List[str], Dict[str, str]]:
    """
    Carga voces desde archivo jerárquico.
    
    Formato:
    ENTIDAD:
      - voz1
      - voz2
    
    Retorna:
    - Lista de voces
    - Mapeo voz_normalizada -> entidad
    """

def load_name_from_csv(
    file_path: str | Path
) -> Tuple[List[str], Dict[str, int]]:
    """
    Carga nombres desde CSV.
    
    Formato:
    termino_normalizado,frecuencia,ejemplo_original
    
    Retorna:
    - Lista de nombres
    - Mapeo nombre -> frecuencia
    """
```

#### 4.2 Exportación

```python
def export_classifications_to_json(
    classifications: List[TermClassification],
    output_path: str | Path,
    indent: int,
    ensure_ascii: bool,
) -> None:
    """Exporta clasificaciones a JSON."""

def export_classifications_by_level(
    classifications: List[TermClassification],
    output_dir: str | Path,
    prefix: str,
) -> Dict[str, Path]:
    """
    Exporta clasificaciones separadas por nivel.
    
    Genera archivos:
    - classification_consensuado.json
    - classification_rechazado.json
    - etc.
    """
```

#### 4.3 Reportes

```python
def generate_summary_report(
    classifications: List[TermClassification],
    total_occurrences: int,
    config: Optional[SimilarityConfig],
) -> Dict[str, Any]:
    """
    Genera reporte estadístico.
    
    Incluye:
    - Conteo por nivel
    - Frecuencias por nivel
    - Porcentajes de cobertura
    - Configuración usada
    """

def export_summary_report(
    report: Dict[str, Any],
    output_path: str | Path,
) -> None:
    """Exporta reporte a JSON."""
```

---

## Flujo de Datos

### Flujo 1: Clasificación Simple

```
Usuario
  │
  ├─> classify_name_json(input_json)
  │     │
  │     ├─> Parsear JSON
  │     ├─> Extraer parámetros
  │     ├─> SimilarityConfig.from_dict() [si hay config]
  │     │
  │     └─> classify_name(name, voices, ...)
  │           │
  │           ├─> Para cada nombre:
  │           │     │
  │           │     ├─> calculate_similarity(term, voices, ...)
  │           │     │     │
  │           │     │     ├─> normalize_text() [si config.normalize]
  │           │     │     │
  │           │     │     ├─> Para cada algoritmo:
  │           │     │     │     │
  │           │     │     │     ├─> levenshtein_ratio_ocr()
  │           │     │     │     ├─> jaro_winkler_similarity()
  │           │     │     │     ├─> ngram_similarity()
  │           │     │     │     │
  │           │     │     │     └─> Evaluar umbral y zona gris
  │           │     │     │
  │           │     │     └─> Retornar Dict[Algo, Result]
  │           │     │
  │           │     ├─> Contar votos
  │           │     ├─> Determinar consenso
  │           │     └─> Clasificar según reglas
  │           │
  │           └─> Retornar List[TermClassification]
  │
  └─> Convertir a JSON y retornar
```

### Flujo 2: Procesamiento por Lotes

```
Usuario
  │
  ├─> process_batch_json(input_json)
  │     │
  │     ├─> Parsear JSON
  │     ├─> Extraer operaciones
  │     ├─> Configuración global (opcional)
  │     │
  │     └─> Para cada operación:
  │           │
  │           ├─> Aplicar config global si no hay local
  │           │
  │           ├─> Ejecutar según tipo:
  │           │     ├─> calculate_similarity_json()
  │           │     ├─> classify_name_json()
  │           │     └─> classify_name_with_report_json()
  │           │
  │           ├─> Capturar resultado o error
  │           │
  │           └─> Agregar a lista de resultados
  │
  └─> Retornar JSON con resumen y resultados
```

---

## Patrones de Diseño

### 1. Strategy Pattern (Algoritmos)

Los algoritmos de similitud implementan el patrón Strategy:

```python
# Cada algoritmo es una estrategia intercambiable
algorithms_map = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: levenshtein_ratio_ocr,
    SimilarityAlgorithm.JARO_WINKLER: jaro_winkler_similarity,
    SimilarityAlgorithm.NGRAM_2: lambda a, b: ngram_similarity(a, b, 2),
}

# Selección dinámica de estrategia
for algo in config.algorithms:
    func = algorithms_map[algo]
    similarity = func(term_norm, voice_norm)
```

### 2. Builder Pattern (Configuración)

`SimilarityConfig` usa el patrón Builder para construcción flexible:

```python
# Construcción por defecto
config = SimilarityConfig()

# Construcción desde diccionario
config = SimilarityConfig.from_dict(data)

# Construcción desde JSON
config = SimilarityConfig.from_json(json_str)
```

### 3. Data Transfer Object (DTO)

Las clases de resultado son DTOs puros:

```python
@dataclass
class SimilarityResult:
    # Solo datos, sin lógica de negocio
    term: str
    voice: str
    similarity: float
    # ...
    
    # Métodos de serialización
    def to_dict() -> Dict
    def to_json() -> str
```

### 4. Facade Pattern (Interfaz JSON)

`json_interface.py` actúa como fachada simplificada:

```python
# Fachada simple
result = classify_name_json(input_json)

# Oculta complejidad interna:
# - Parseo JSON
# - Creación de configuración
# - Llamadas a múltiples funciones
# - Serialización de resultados
```

### 5. Template Method (Clasificación)

El proceso de clasificación sigue Template Method:

```python
def classify_name(...):
    # Plantilla del algoritmo
    for term in name:
        # 1. Calcular similitud (paso variable)
        results = calculate_similarity(...)
        
        # 2. Contar votos (paso fijo)
        votes = _count_votes(results)
        
        # 3. Determinar consenso (paso fijo)
        consensus = _determine_consensus(results)
        
        # 4. Clasificar (paso variable según config)
        level = _classify_term(votes, consensus, config)
```

---

## Principios de Diseño

### 1. Separación de Responsabilidades (SRP)

Cada módulo tiene una responsabilidad única:
- `algorithms.py`: Solo algoritmos matemáticos
- `similarity.py`: Solo lógica de clasificación
- `json_interface.py`: Solo interfaz JSON
- `utils.py`: Solo utilidades I/O

### 2. Abierto/Cerrado (OCP)

Fácil agregar nuevos algoritmos sin modificar código existente:

```python
# Agregar nuevo algoritmo:
# 1. Implementar función en algorithms.py
def new_algorithm(a: str, b: str) -> float:
    # implementación
    pass

# 2. Agregar a enumeración
class SimilarityAlgorithm(Enum):
    NEW_ALGO = "new_algo"

# 3. Agregar umbral por defecto
DEFAULT_THRESHOLDS[SimilarityAlgorithm.NEW_ALGO] = 0.80

# 4. Listo para usar
```

### 3. Inversión de Dependencias (DIP)

Las capas superiores dependen de abstracciones:

```python
# similarity.py no depende de json_interface.py
# json_interface.py depende de similarity.py (abstracción)

# Permite usar similarity.py sin JSON:
from portada_s_index.similarity import classify_name

results = classify_name(name, voices)  # Sin JSON
```

### 4. Composición sobre Herencia

Uso de composición en lugar de herencia:

```python
# No hay jerarquías de clases complejas
# Se componen objetos simples:

@dataclass
class TermClassification:
    results: Dict[SimilarityAlgorithm, SimilarityResult]  # Composición
    classification: ClassificationLevel  # Composición
```

### 5. Inmutabilidad

Uso de dataclasses inmutables cuando es posible:

```python
@dataclass(frozen=True)  # Inmutable
class SimilarityResult:
    term: str
    voice: str
    similarity: float
```

---

## Extensibilidad

### Agregar Nuevo Algoritmo

```python
# 1. Implementar en algorithms.py
def cosine_similarity(a: str, b: str) -> float:
    # implementación
    return similarity_value

# 2. Agregar a enumeración
class SimilarityAlgorithm(Enum):
    COSINE = "cosine"

# 3. Configurar umbrales
DEFAULT_THRESHOLDS[SimilarityAlgorithm.COSINE] = 0.75
DEFAULT_GRAY_ZONES[SimilarityAlgorithm.COSINE] = (0.70, 0.749)

# 4. Usar
config = SimilarityConfig(
    algorithms=[SimilarityAlgorithm.COSINE]
)
```

### Agregar Nuevo Nivel de Clasificación

```python
# 1. Agregar a enumeración
class ClassificationLevel(Enum):
    ALTA_PRECISION = "ALTA_PRECISION"

# 2. Modificar lógica de clasificación
def _classify_term(...):
    if votes_entity >= 4 and all_algorithms_agree:
        return ClassificationLevel.ALTA_PRECISION
    # ...
```

### Agregar Nueva Operación de Lote

```python
# En json_interface.py
def new_operation_json(input_json: str | Dict) -> str:
    # implementación
    pass

# En process_batch_json()
elif op_type == "new_operation":
    result = new_operation_json(op_data)
```

---

## Consideraciones de Rendimiento

### 1. Normalización de Texto

```python
# Cache de normalizaciones para evitar recálculos
_normalization_cache = {}

def normalize_text(text: str) -> str:
    if text in _normalization_cache:
        return _normalization_cache[text]
    
    normalized = _normalize(text)
    _normalization_cache[text] = normalized
    return normalized
```

### 2. Algoritmos Optimizados

- Levenshtein usa programación dinámica (O(n*m))
- Jaro-Winkler optimizado para prefijos
- N-gramas usa sets para intersección rápida

### 3. Procesamiento por Lotes

```python
# Procesa múltiples operaciones en una llamada
# Reduce overhead de serialización JSON
process_batch_json({
    "operations": [op1, op2, op3, ...]
})
```

---

## Testing

### Estructura de Tests

```
tests/
├── test_algorithms.py      # Tests unitarios de algoritmos
├── test_similarity.py       # Tests de lógica de negocio
├── test_json_interface.py   # Tests de interfaz JSON
└── test_utils.py           # Tests de utilidades

# Tests externos
test_portada_external.py    # Simulación de uso real
test_real_data.py          # Tests con datos históricos
```

### Estrategia de Testing

1. **Unitarios**: Cada algoritmo individualmente
2. **Integración**: Flujo completo de clasificación
3. **Externos**: Uso desde fuera del paquete
4. **Datos reales**: Validación con datos históricos

---

## Dependencias

### Dependencias de Producción

**Ninguna** - Solo biblioteca estándar de Python:
- `json`: Serialización JSON
- `dataclasses`: Clases de datos
- `enum`: Enumeraciones
- `typing`: Type hints
- `pathlib`: Manejo de rutas
- `unicodedata`: Normalización Unicode

### Dependencias de Desarrollo

```toml
[tool.hatch.envs.default]
dependencies = [
    "pytest>=7.0",
    "black>=23.0",
    "mypy>=1.0",
]
```

---

## Versionado Semántico

```
MAJOR.MINOR.PATCH

MAJOR: Cambios incompatibles en API
MINOR: Nueva funcionalidad compatible
PATCH: Correcciones de bugs
```

**Ejemplo**:
- `0.1.0`: Versión inicial
- `0.2.0`: Cambio de terminología (breaking change en salida JSON)
- `0.2.1`: Corrección de bug en normalización

---

## Conclusión

La arquitectura de Portada S-Index está diseñada para ser:

✅ **Modular**: Capas claramente separadas  
✅ **Extensible**: Fácil agregar algoritmos y funcionalidad  
✅ **Testeable**: Funciones puras y sin dependencias  
✅ **Mantenible**: Código limpio y bien documentado  
✅ **Eficiente**: Sin dependencias externas, optimizado  
✅ **Flexible**: Configuración completa vía JSON  

Esta arquitectura permite evolucionar la biblioteca sin romper compatibilidad y facilita la contribución de nuevos desarrolladores.
