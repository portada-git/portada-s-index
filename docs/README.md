# Documentación de Portada S-Index

Bienvenido a la documentación completa de Portada S-Index, una biblioteca Python para desambiguación de nombres históricos mediante algoritmos de similitud de cadenas.

## 📑 Índice de Documentación

### Para Usuarios

1. **[../README.md](../README.md)** - Inicio rápido y visión general
   - Instalación
   - Ejemplos de uso
   - Características principales
   - Resultados con datos reales

2. **[JSON_GUIDE.md](JSON_GUIDE.md)** - Guía completa de JSON
   - Formatos de entrada y salida
   - Ejemplos de todos los casos de uso
   - Referencia de parámetros
   - Procesamiento por lotes

3. **[INSTALL.md](INSTALL.md)** - Guía de instalación
   - Requisitos del sistema
   - Instalación con pip/uv
   - Instalación desde código fuente
   - Verificación de instalación

### Para Desarrolladores

4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura del paquete
   - Visión general de la arquitectura
   - Estructura de módulos
   - Flujo de datos
   - Patrones de diseño
   - Principios de diseño
   - Extensibilidad

5. **[API.md](API.md)** - Referencia de API
   - Módulos y funciones
   - Clases y enumeraciones
   - Algoritmos de bajo nivel
   - Utilidades
   - Ejemplos de código

6. **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios
   - Versiones publicadas
   - Nuevas características
   - Correcciones de bugs
   - Cambios incompatibles

## 🎯 Guías por Caso de Uso

### Quiero empezar rápidamente
→ Lee [../README.md](../README.md) sección "Uso Rápido"

### Quiero entender los formatos JSON
→ Lee [JSON_GUIDE.md](JSON_GUIDE.md)

### Quiero usar la API de Python directamente
→ Lee [API.md](API.md)

### Quiero contribuir al proyecto
→ Lee [ARCHITECTURE.md](ARCHITECTURE.md)

### Quiero instalar en producción
→ Lee [INSTALL.md](INSTALL.md)

### Quiero saber qué cambió en cada versión
→ Lee [CHANGELOG.md](CHANGELOG.md)

## 📊 Estructura del Proyecto

```
portada-s-index/
├── src/
│   └── portada_s_index/
│       ├── __init__.py           # Exportaciones públicas
│       ├── algorithms.py         # Algoritmos de similitud
│       ├── similarity.py         # Lógica de clasificación
│       ├── json_interface.py     # Interfaz JSON
│       └── utils.py             # Utilidades I/O
├── docs/
│   ├── README.md                # Este archivo
│   ├── ARCHITECTURE.md          # Arquitectura
│   ├── API.md                   # Referencia API
│   ├── JSON_GUIDE.md            # Guía JSON
│   ├── INSTALL.md               # Instalación
│   └── CHANGELOG.md             # Cambios
├── tests/
│   └── test_basic.py            # Tests unitarios
├── examples/                     # Ejemplos de uso
├── pyproject.toml               # Configuración del paquete
└── README.md                    # Documentación principal
```

## 🔍 Conceptos Clave

### Algoritmos de Similitud

La biblioteca implementa 5 algoritmos de similitud de cadenas:

1. **Levenshtein OCR**: Distancia de edición con corrección para errores de OCR
2. **Levenshtein Ratio**: Distancia de edición estándar normalizada
3. **Jaro-Winkler**: Optimizado para nombres propios con énfasis en prefijos
4. **N-gramas 2**: Similitud basada en bigramas
5. **N-gramas 3**: Similitud basada en trigramas

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles de implementación.

### Sistema de Clasificación

Los nombres se clasifican en 5 niveles de confianza:

| Nivel | Descripción | Uso |
|-------|-------------|-----|
| **CONSENSUADO** | Alta confianza | Usar directamente |
| **CONSENSUADO_DEBIL** | Confianza moderada | Revisar casos críticos |
| **SOLO_1_VOTO** | Baja confianza | Requiere revisión manual |
| **ZONA_GRIS** | Ambiguo | Requiere revisión manual |
| **RECHAZADO** | Sin correspondencia | Investigar o descartar |

Ver [API.md](API.md) para detalles de cada nivel.

### Interfaz JSON

Toda la entrada y salida se maneja mediante JSON:

```python
# Entrada
{
  "names": ["aleman", "frances"],
  "voices": ["aleman", "frances"]
}

# Salida
{
  "total_names": 2,
  "classifications": [...]
}
```

Ver [JSON_GUIDE.md](JSON_GUIDE.md) para todos los formatos.

## 🛠️ Configuración

La biblioteca es altamente configurable:

```python
{
  "config": {
    "algorithms": ["levenshtein_ocr", "jaro_winkler"],
    "thresholds": {
      "levenshtein_ocr": 0.80,
      "jaro_winkler": 0.90
    },
    "normalize": true,
    "min_votes_consensus": 2,
    "require_levenshtein_ocr": true
  }
}
```

Ver [JSON_GUIDE.md](JSON_GUIDE.md) sección "Configuración" para detalles.

## 📈 Rendimiento

Con datos reales del proyecto PORTADA:

- **100 nombres** procesados en **< 1 segundo**
- **99.68%** de cobertura consensuada
- **110,924 ocurrencias** clasificadas correctamente

Ver [../README.md](../README.md) sección "Resultados con Datos Reales".

## 🤝 Contribuir

Para contribuir al proyecto:

1. Lee [ARCHITECTURE.md](ARCHITECTURE.md) para entender el diseño
2. Lee [API.md](API.md) para conocer la API interna
3. Revisa [CHANGELOG.md](CHANGELOG.md) para ver el historial
4. Sigue los principios de diseño documentados

## 📝 Licencia

[Especificar licencia]

## 📧 Soporte

Para preguntas o problemas:
- Abre un issue en el repositorio
- Consulta la documentación relevante
- Revisa los ejemplos en `examples/`

---

**Última actualización**: 2026  
**Versión**: 0.2.0
