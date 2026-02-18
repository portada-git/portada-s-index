"""
Interfaz JSON para portada-s-index.
Todas las entradas y salidas se manejan mediante JSON.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .similarity import (
    SimilarityAlgorithm,
    SimilarityConfig,
    ClassificationLevel,
    calculate_similarity,
    classify_terms,
)


# =============================================================================
# FUNCIONES DE ENTRADA JSON
# =============================================================================

def calculate_similarity_json(input_json: str | Dict[str, Any]) -> str:
    """
    Calcula similitud desde entrada JSON.
    
    Formato de entrada:
    {
        "term": "alemán",
        "voices": ["aleman", "alemana", "frances"],
        "config": {  // opcional
            "algorithms": ["levenshtein_ocr", "jaro_winkler"],
            "thresholds": {"levenshtein_ocr": 0.80},
            "normalize": true
        },
        "voice_to_entity": {  // opcional
            "aleman": "ALEMANIA",
            "alemana": "ALEMANIA"
        }
    }
    
    Args:
        input_json: String JSON o diccionario con los datos de entrada
    
    Returns:
        String JSON con los resultados
    """
    # Parsear entrada si es string
    if isinstance(input_json, str):
        data = json.loads(input_json)
    else:
        data = input_json
    
    # Extraer parámetros
    term = data["term"]
    voices = data["voices"]
    
    # Configuración opcional
    config = None
    if "config" in data:
        config = SimilarityConfig.from_dict(data["config"])
    
    # Mapeo de voces opcional
    voice_to_entity = data.get("voice_to_entity", None)
    
    # Calcular similitud
    results = calculate_similarity(term, voices, config, voice_to_entity)
    
    # Convertir a formato JSON
    output = {
        "term": term,
        "results": {
            algo.value: result.to_dict()
            for algo, result in results.items()
        }
    }
    
    return json.dumps(output, ensure_ascii=False)


def classify_terms_json(input_json: str | Dict[str, Any]) -> str:
    """
    Clasifica términos desde entrada JSON.
    
    Formato de entrada:
    {
        "terms": ["aleman", "frances", "ingles"],
        "voices": ["aleman", "alemana", "frances", "francesa"],
        "frequencies": {  // opcional
            "aleman": 100,
            "frances": 80
        },
        "config": {  // opcional
            "algorithms": ["levenshtein_ocr", "jaro_winkler"],
            "thresholds": {"levenshtein_ocr": 0.80},
            "normalize": true
        },
        "voice_to_entity": {  // opcional
            "aleman": "ALEMANIA",
            "alemana": "ALEMANIA"
        }
    }
    
    Args:
        input_json: String JSON o diccionario con los datos de entrada
    
    Returns:
        String JSON con las clasificaciones
    """
    # Parsear entrada si es string
    if isinstance(input_json, str):
        data = json.loads(input_json)
    else:
        data = input_json
    
    # Extraer parámetros
    terms = data["terms"]
    voices = data["voices"]
    frequencies = data.get("frequencies", None)
    
    # Configuración opcional
    config = None
    if "config" in data:
        config = SimilarityConfig.from_dict(data["config"])
    
    # Mapeo de voces opcional
    voice_to_entity = data.get("voice_to_entity", None)
    
    # Clasificar términos
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        config=config,
        voice_to_entity=voice_to_entity,
    )
    
    # Convertir a formato JSON
    output = {
        "total_terms": len(classifications),
        "classifications": [c.to_dict() for c in classifications]
    }
    
    return json.dumps(output, ensure_ascii=False)


def classify_terms_with_report_json(input_json: str | Dict[str, Any]) -> str:
    """
    Clasifica términos y genera reporte desde entrada JSON.
    
    Formato de entrada: igual que classify_terms_json
    
    Args:
        input_json: String JSON o diccionario con los datos de entrada
    
    Returns:
        String JSON con clasificaciones y reporte resumen
    """
    # Parsear entrada si es string
    if isinstance(input_json, str):
        data = json.loads(input_json)
    else:
        data = input_json
    
    # Extraer parámetros
    terms = data["terms"]
    voices = data["voices"]
    frequencies = data.get("frequencies", None)
    
    # Configuración opcional
    config = None
    if "config" in data:
        config = SimilarityConfig.from_dict(data["config"])
    
    # Mapeo de voces opcional
    voice_to_entity = data.get("voice_to_entity", None)
    
    # Clasificar términos
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        config=config,
        voice_to_entity=voice_to_entity,
    )
    
    # Generar reporte
    from .utils import generate_summary_report
    
    total_occurrences = sum(frequencies.values()) if frequencies else len(terms)
    report = generate_summary_report(classifications, total_occurrences, config)
    
    # Convertir a formato JSON
    output = {
        "report": report,
        "classifications": [c.to_dict() for c in classifications]
    }
    
    return json.dumps(output, ensure_ascii=False)


# =============================================================================
# FUNCIONES DE ARCHIVO JSON
# =============================================================================

def calculate_similarity_from_file(input_file: str | Path, output_file: Optional[str | Path] = None) -> str:
    """
    Calcula similitud desde archivo JSON de entrada.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida (opcional)
    
    Returns:
        String JSON con los resultados
    """
    input_file = Path(input_file)
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result_json = calculate_similarity_json(data)
    
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_json)
    
    return result_json


def classify_terms_from_file(input_file: str | Path, output_file: Optional[str | Path] = None) -> str:
    """
    Clasifica términos desde archivo JSON de entrada.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida (opcional)
    
    Returns:
        String JSON con las clasificaciones
    """
    input_file = Path(input_file)
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result_json = classify_terms_json(data)
    
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_json)
    
    return result_json


def classify_terms_with_report_from_file(
    input_file: str | Path,
    output_file: Optional[str | Path] = None
) -> str:
    """
    Clasifica términos y genera reporte desde archivo JSON de entrada.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida (opcional)
    
    Returns:
        String JSON con clasificaciones y reporte
    """
    input_file = Path(input_file)
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result_json = classify_terms_with_report_json(data)
    
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_json)
    
    return result_json


# =============================================================================
# FUNCIONES DE PROCESAMIENTO POR LOTES
# =============================================================================

def process_batch_json(input_json: str | Dict[str, Any]) -> str:
    """
    Procesa múltiples operaciones en lote desde JSON.
    
    Formato de entrada:
    {
        "operations": [
            {
                "type": "calculate_similarity",
                "data": {
                    "term": "alemán",
                    "voices": ["aleman", "alemana"]
                }
            },
            {
                "type": "classify_terms",
                "data": {
                    "terms": ["aleman", "frances"],
                    "voices": ["aleman", "frances"]
                }
            }
        ],
        "config": {  // configuración global opcional
            "algorithms": ["levenshtein_ocr"],
            "normalize": true
        }
    }
    
    Args:
        input_json: String JSON o diccionario con las operaciones
    
    Returns:
        String JSON con los resultados de todas las operaciones
    """
    # Parsear entrada si es string
    if isinstance(input_json, str):
        data = json.loads(input_json)
    else:
        data = input_json
    
    operations = data["operations"]
    global_config = data.get("config", None)
    
    results = []
    
    for i, operation in enumerate(operations):
        op_type = operation["type"]
        op_data = operation["data"]
        
        # Aplicar configuración global si no hay local
        if global_config and "config" not in op_data:
            op_data["config"] = global_config
        
        try:
            if op_type == "calculate_similarity":
                result = calculate_similarity_json(op_data)
                results.append({
                    "operation_index": i,
                    "type": op_type,
                    "status": "success",
                    "result": json.loads(result)
                })
            elif op_type == "classify_terms":
                result = classify_terms_json(op_data)
                results.append({
                    "operation_index": i,
                    "type": op_type,
                    "status": "success",
                    "result": json.loads(result)
                })
            elif op_type == "classify_with_report":
                result = classify_terms_with_report_json(op_data)
                results.append({
                    "operation_index": i,
                    "type": op_type,
                    "status": "success",
                    "result": json.loads(result)
                })
            else:
                results.append({
                    "operation_index": i,
                    "type": op_type,
                    "status": "error",
                    "error": f"Unknown operation type: {op_type}"
                })
        except Exception as e:
            results.append({
                "operation_index": i,
                "type": op_type,
                "status": "error",
                "error": str(e)
            })
    
    output = {
        "total_operations": len(operations),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }
    
    return json.dumps(output, ensure_ascii=False)


def process_batch_from_file(input_file: str | Path, output_file: Optional[str | Path] = None) -> str:
    """
    Procesa lote desde archivo JSON.
    
    Args:
        input_file: Ruta al archivo JSON de entrada
        output_file: Ruta al archivo JSON de salida (opcional)
    
    Returns:
        String JSON con los resultados
    """
    input_file = Path(input_file)
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    result_json = process_batch_json(data)
    
    if output_file:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_json)
    
    return result_json
