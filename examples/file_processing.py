"""
Ejemplo de procesamiento de archivos con portada-s-index.
"""

import json
from pathlib import Path
from portada_s_index import (
    SimilarityAlgorithm,
    SimilarityConfig,
    classify_terms,
    load_voices_from_file,
    load_terms_from_csv,
    export_classifications_to_json,
    export_classifications_by_level,
    generate_summary_report,
    export_summary_report,
)


def process_field(
    voices_file: str,
    terms_file: str,
    output_dir: str,
    field_name: str,
):
    """
    Procesa un campo completo: carga datos, clasifica y exporta resultados.
    
    Args:
        voices_file: Ruta al archivo de voces
        terms_file: Ruta al archivo CSV de términos
        output_dir: Directorio de salida
        field_name: Nombre del campo (para nombres de archivo)
    """
    print(f"Procesando campo: {field_name}")
    print("=" * 70)
    
    # 1. Cargar voces
    print("\n1. Cargando voces...")
    voices, voice_to_entity = load_voices_from_file(voices_file)
    print(f"   Cargadas {len(voices)} voces")
    print(f"   Entidades: {len(set(voice_to_entity.values()))}")
    
    # 2. Cargar términos
    print("\n2. Cargando términos...")
    terms, frequencies = load_terms_from_csv(terms_file)
    total_occurrences = sum(frequencies.values())
    print(f"   Términos únicos: {len(terms)}")
    print(f"   Ocurrencias totales: {total_occurrences:,}")
    
    # 3. Configurar algoritmos
    print("\n3. Configurando algoritmos...")
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
            SimilarityAlgorithm.NGRAM_2,
        ],
        normalize=True,
    )
    print(f"   Algoritmos: {[a.value for a in config.algorithms]}")
    
    # 4. Clasificar términos
    print("\n4. Clasificando términos...")
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        config=config,
        voice_to_entity=voice_to_entity,
    )
    print(f"   Clasificados: {len(classifications)} términos")
    
    # 5. Generar reporte resumen
    print("\n5. Generando reporte resumen...")
    report = generate_summary_report(
        classifications=classifications,
        total_occurrences=total_occurrences,
        config=config,
    )
    
    print("\n   Distribución por nivel:")
    for level, stats in report["by_level"].items():
        print(f"     {level}: {stats['count']} términos ({stats['percentage']:.2f}%)")
    
    print(f"\n   Cobertura consensuada (estricta): {report['coverage']['consensuado_strict']['percentage']:.2f}%")
    print(f"   Cobertura consensuada (total): {report['coverage']['consensuado_total']['percentage']:.2f}%")
    
    # 6. Exportar resultados
    print("\n6. Exportando resultados...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Exportar clasificación completa
    complete_file = output_path / f"classification_complete_{field_name}.json"
    export_classifications_to_json(classifications, complete_file)
    print(f"   ✓ {complete_file}")
    
    # Exportar por nivel
    level_files = export_classifications_by_level(
        classifications=classifications,
        output_dir=output_path,
        prefix=f"classification_{field_name}",
    )
    for level, file_path in level_files.items():
        print(f"   ✓ {file_path}")
    
    # Exportar reporte
    report_file = output_path / f"report_{field_name}.json"
    export_summary_report(report, report_file)
    print(f"   ✓ {report_file}")
    
    print("\n✓ Procesamiento completado")
    print("=" * 70)


def example_complete_workflow():
    """Ejemplo de flujo completo de procesamiento."""
    
    # Rutas de ejemplo (ajustar según tu estructura)
    base_dir = Path(__file__).parent.parent.parent / "similitudes"
    
    # Procesar campo de banderas
    process_field(
        voices_file=str(base_dir / "listas" / "lista_banderas.txt"),
        terms_file=str(base_dir / "datos" / "terminos_ship_flag.csv"),
        output_dir="output/ship_flag",
        field_name="ship_flag",
    )


def example_custom_processing():
    """Ejemplo con procesamiento personalizado."""
    print("Ejemplo de procesamiento personalizado")
    print("=" * 70)
    
    # Datos de ejemplo en memoria
    terms = ["aleman", "frances", "ingles", "italiano", "desconocido"]
    voices = ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa", "italiano", "italiana"]
    frequencies = {"aleman": 100, "frances": 80, "ingles": 150, "italiano": 90, "desconocido": 5}
    
    voice_to_entity = {
        "aleman": "ALEMANIA",
        "alemana": "ALEMANIA",
        "frances": "FRANCIA",
        "francesa": "FRANCIA",
        "ingles": "INGLATERRA",
        "inglesa": "INGLATERRA",
        "italiano": "ITALIA",
        "italiana": "ITALIA",
    }
    
    # Configuración personalizada
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
        ],
        thresholds={
            SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.80,
            SimilarityAlgorithm.JARO_WINKLER: 0.85,
        },
        min_votes_consensus=2,
        require_levenshtein_ocr=True,
    )
    
    # Clasificar
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        config=config,
        voice_to_entity=voice_to_entity,
    )
    
    # Exportar
    output_dir = Path("output/custom")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    export_classifications_to_json(
        classifications,
        output_dir / "classifications.json",
    )
    
    # Generar y exportar reporte
    total_occurrences = sum(frequencies.values())
    report = generate_summary_report(classifications, total_occurrences, config)
    export_summary_report(report, output_dir / "report.json")
    
    print("\n✓ Resultados exportados a:", output_dir)
    print("\nReporte resumen:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Descomentar el ejemplo que quieras ejecutar
    
    # example_complete_workflow()
    
    example_custom_processing()
