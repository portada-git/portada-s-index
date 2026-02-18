"""
Utilidades para carga de datos y exportación de resultados.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from .similarity import normalize_text


def load_voices_from_file(file_path: str | Path) -> Tuple[List[str], Dict[str, str]]:
    """
    Carga voces desde un archivo de lista jerárquico.
    
    Formato esperado:
        ENTIDAD:
          - voz1
          - voz2
        
        OTRA_ENTIDAD:
          - voz_a
    
    Args:
        file_path: Ruta al archivo de voces
    
    Returns:
        Tupla con:
        - Lista de voces
        - Diccionario de voz_normalizada -> entidad
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
    
    voices = []
    voice_to_entity = {}
    current_entity = None
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            
            if not line.strip():
                continue
            
            # Línea de entidad (termina en :)
            if line.strip().endswith(":") and not line.startswith(" "):
                current_entity = line.strip()[:-1]
                continue
            
            # Línea de voz (empieza con -)
            if line.strip().startswith("-"):
                voice = line.strip()[1:].strip()
                if voice:
                    voices.append(voice)
                    voice_norm = normalize_text(voice)
                    if voice_norm and current_entity:
                        voice_to_entity[voice_norm] = current_entity
    
    return voices, voice_to_entity


def load_terms_from_csv(file_path: str | Path) -> Tuple[List[str], Dict[str, int]]:
    """
    Carga nombres desde un archivo CSV.
    
    Formato esperado (con encabezado):
        termino_normalizado,frecuencia,ejemplo_original
        termino1,100,Termino1
        termino2,50,Término2
    
    Args:
        file_path: Ruta al archivo CSV
    
    Returns:
        Tupla con:
        - Lista de nombres únicos
        - Diccionario de nombre -> frecuencia
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
    
    terms = []
    frequencies = {}
    
    with open(file_path, "r", encoding="utf-8-sig") as f:
        # Saltar encabezado
        next(f)
        
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(",")
            if len(parts) >= 2:
                term = parts[0].strip()
                try:
                    freq = int(parts[1].strip())
                except ValueError:
                    freq = 1
                
                terms.append(term)
                frequencies[term] = freq
    
    return terms, frequencies


def export_classifications_to_json(
    classifications: List[Any],
    output_path: str | Path,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """
    Exporta clasificaciones a un archivo JSON.
    
    Args:
        classifications: Lista de objetos TermClassification
        output_path: Ruta del archivo de salida
        indent: Indentación del JSON (default: 2)
        ensure_ascii: Si se debe escapar caracteres no-ASCII (default: False)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = [c.to_dict() for c in classifications]
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def export_classifications_by_level(
    classifications: List[Any],
    output_dir: str | Path,
    prefix: str = "classification",
    indent: int = 2,
) -> Dict[str, Path]:
    """
    Exporta clasificaciones separadas por nivel a archivos JSON individuales.
    
    Args:
        classifications: Lista de objetos TermClassification
        output_dir: Directorio de salida
        prefix: Prefijo para nombres de archivo (default: "classification")
        indent: Indentación del JSON (default: 2)
    
    Returns:
        Diccionario con nivel -> ruta del archivo generado
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Agrupar por nivel
    by_level: Dict[str, List[Any]] = {}
    for classification in classifications:
        level = classification.classification.value
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(classification)
    
    # Exportar cada nivel
    output_files = {}
    for level, items in by_level.items():
        file_name = f"{prefix}_{level.lower()}.json"
        file_path = output_dir / file_name
        export_classifications_to_json(items, file_path, indent=indent)
        output_files[level] = file_path
    
    return output_files


def generate_summary_report(
    classifications: List[Any],
    total_occurrences: int,
    config: Any = None,
) -> Dict[str, Any]:
    """
    Genera un reporte resumen de las clasificaciones.
    
    Args:
        classifications: Lista de objetos TermClassification
        total_occurrences: Total de ocurrencias en los datos originales
        config: Configuración usada (opcional)
    
    Returns:
        Diccionario con estadísticas del reporte
    """
    from collections import Counter
    
    # Contar por nivel
    level_counts = Counter(c.classification.value for c in classifications)
    
    # Calcular frecuencias por nivel
    level_frequencies = {}
    for level in level_counts:
        freq = sum(
            c.frequency for c in classifications 
            if c.classification.value == level
        )
        level_frequencies[level] = freq
    
    # Calcular porcentajes
    level_percentages = {
        level: (freq / total_occurrences * 100) if total_occurrences > 0 else 0
        for level, freq in level_frequencies.items()
    }
    
    # Estadísticas generales
    consensuado_freq = level_frequencies.get("CONSENSUADO", 0)
    consensuado_debil_freq = level_frequencies.get("CONSENSUADO_DEBIL", 0)
    
    report = {
        "total_names": len(classifications),
        "total_occurrences": total_occurrences,
        "by_level": {
            level: {
                "count": level_counts[level],
                "occurrences": level_frequencies[level],
                "percentage": round(level_percentages[level], 2),
            }
            for level in level_counts
        },
        "coverage": {
            "consensuado_strict": {
                "occurrences": consensuado_freq,
                "percentage": round(
                    (consensuado_freq / total_occurrences * 100) if total_occurrences > 0 else 0,
                    2
                ),
            },
            "consensuado_total": {
                "occurrences": consensuado_freq + consensuado_debil_freq,
                "percentage": round(
                    ((consensuado_freq + consensuado_debil_freq) / total_occurrences * 100)
                    if total_occurrences > 0 else 0,
                    2
                ),
            },
        },
    }
    
    # Agregar configuración si está disponible
    if config:
        report["config"] = config.to_dict() if hasattr(config, "to_dict") else str(config)
    
    return report


def export_summary_report(
    report: Dict[str, Any],
    output_path: str | Path,
    indent: int = 2,
) -> None:
    """
    Exporta el reporte resumen a un archivo JSON.
    
    Args:
        report: Diccionario con el reporte
        output_path: Ruta del archivo de salida
        indent: Indentación del JSON (default: 2)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=indent, ensure_ascii=False)
