# Changelog

## [0.1.0] - 2024

### Añadido
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
- Utilidades de I/O:
  - Carga de archivos de voces jerárquicos
  - Carga de términos desde CSV
  - Exportación de clasificaciones a JSON
  - Exportación por niveles de clasificación
  - Generación de reportes resumen
- Ejemplos de uso:
  - basic_usage.py: Ejemplos básicos
  - file_processing.py: Procesamiento de archivos
  - quick_test.py: Tests rápidos sin instalación
- Documentación completa:
  - README.md: Documentación general
  - API.md: Referencia de API
  - INSTALL.md: Guía de instalación
- Tests unitarios básicos

### Características técnicas
- Sin dependencias externas (solo biblioteca estándar de Python)
- Compatible con Python >= 3.12
- Soporte completo para serialización JSON
- Mapeo de voces a entidades para agrupación
- Sistema de votación por consenso entre algoritmos
- Grupos de confusión OCR predefinidos

### Notas
- Versión inicial extraída del proyecto similitudes
- Diseñada para el proyecto PORTADA de desambiguación de términos históricos
