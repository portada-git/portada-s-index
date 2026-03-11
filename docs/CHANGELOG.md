# Changelog

## [0.2.0] - 2026 (Próxima versión)

### Añadido

- **DOCUMENTACIÓN DE ARQUITECTURA**: Nueva documentación completa
  - `docs/ARCHITECTURE.md`: Arquitectura detallada del paquete
  - `docs/README.md`: Índice de toda la documentación
  - Diagramas de flujo de datos
  - Patrones de diseño utilizados
  - Guía de extensibilidad
  - Principios de diseño aplicados

### Cambiado

- **BREAKING CHANGE**: Cambio de terminología en toda la biblioteca
  - "términos" → "nombres" en toda la documentación y ejemplos
  - La interfaz JSON ahora acepta `"name"` en lugar de `"name"` (mantiene retrocompatibilidad con `"name"`)
  - La salida JSON usa `"total_name"` en lugar de `"total_name"`
  - Actualización completa de README.md, JSON_GUIDE.md y API.md
  - "voces" se mantiene sin cambios
  - Razón: Mayor claridad semántica para el dominio de aplicación (nombres históricos)

### Retrocompatibilidad

- La entrada JSON sigue aceptando `"name"` por compatibilidad con código existente
- Se recomienda migrar a `"name"` en nuevas implementaciones

## [0.1.0] - 2026

### Añadido

- **INTERFAZ JSON**: Entrada y salida exclusivamente mediante JSON
  - `calculate_similarity_json()`: Calcular similitud desde JSON
  - `classify_name_json()`: Clasificar términos desde JSON
  - `classify_name_with_report_json()`: Clasificar con reporte desde JSON
  - `process_batch_json()`: Procesamiento por lotes desde JSON
  - Funciones `*_from_file()` para procesar archivos JSON
- Implementación inicial de la biblioteca portada-s-index
- 5 algoritmos de similitud:
  - Levenshtein estándar
  - Levenshtein con corrección OCR
  - Jaro-Winkler
  - N-gramas (bigramas y trigramas)
- Sistema de clasificación con 5 niveles:
  - CONSENSUADO
  - CONSENSUADO_DEBIL
  - SOLO_1_VOTO
  - ZONA_GRIS
  - RECHAZADO
- Configuración flexible con umbrales y zonas grises personalizables
- Normalización automática de texto (Unicode, diacríticos, minúsculas)
- Salida completa en formato JSON
- Procesamiento por lotes (múltiples operaciones en una llamada)
- Utilidades de I/O (uso interno):
  - Carga de archivos de voces jerárquicos
  - Carga de términos desde CSV
  - Exportación de clasificaciones a JSON
  - Exportación por niveles de clasificación
  - Generación de reportes resumen
- Ejemplos de uso:
  - json_usage.py: Ejemplos con JSON en memoria
  - json_file_processing.py: Procesamiento de archivos JSON
  - input\_\*.json: Archivos de ejemplo de entrada
  - output\_\*.json: Archivos de ejemplo de salida
- Documentación completa:
  - README.md: Documentación general con enfoque JSON
  - JSON_GUIDE.md: Guía completa de formatos JSON
  - API.md: Referencia de API
  - INSTALL.md: Guía de instalación
- Tests unitarios básicos

### Características técnicas

- Sin dependencias externas (solo biblioteca estándar de Python)
- Compatible con Python >= 3.12
- Soporte completo para serialización JSON
- Entrada JSON como diccionario o string
- Procesamiento de archivos JSON con salida opcional
- Mapeo de voces a entidades para agrupación
- Sistema de votación por consenso entre algoritmos
- Grupos de confusión OCR predefinidos
- Manejo de errores en procesamiento por lotes

### Notas

- Versión inicial extraída del proyecto portada_s_index
- Diseñada para el proyecto PORTADA de desambiguación de términos históricos
- Interfaz principal: JSON (entrada y salida)
