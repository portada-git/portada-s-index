from portada_s_index import (
    PortAdaSIndex,
    SimilarityConfig,
    SimilarityAlgorithm
)
import os

def demo_workflow():
    print("1. ETAPA DE CONFIGURACIÓN")
    # Configuración personalizada con algoritmos y sus umbrales (límites)
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
            SimilarityAlgorithm.NGRAM_2
        ],
        thresholds={
            SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.80,
            SimilarityAlgorithm.JARO_WINKLER: 0.85,
            SimilarityAlgorithm.NGRAM_2: 0.70
        }
    )
    
    # Inicializar la librería
    s_index = PortAdaSIndex(config=config)
    s_index.set_entity_type("Geografía")

    print("\n2. ETAPA DE CARGA DE DATOS")
    # Simular carga desde archivos (creamos archivos temporales para el demo)
    voices_path = "voices_demo.txt"
    with open(voices_path, "w", encoding="utf-8") as f:
        f.write("ALEMANIA:\n  - aleman\n  - alemana\n  - prusia\n")
        f.write("FRANCIA:\n  - frances\n  - francesa\n  - galia\n")
        
    citations_path = "citations_demo.csv"
    with open(citations_path, "w", encoding="utf-8") as f:
        f.write("termino_normalizado,frecuencia,ejemplo\n")
        f.write("aleman,100,Aleman\n")
        f.write("frances,85,Frances\n")
        f.write("alemona,10,Alemona\n") # Error OCR
        f.write("prusia,5,Prusia\n")
        
    s_index.load_known_entities_from_file(voices_path)
    s_index.load_citations_from_csv(citations_path)

    print("\n3. ETAPA DE PREPROCESAMIENTO (FIT) CON CACHE")
    # El método fit calcula los vectores/prepara los datos y los guarda en disco
    cache_file = "portada_cache.pkl"
    s_index.fit(cache_path=cache_file)
    print(f"Caché generada en: {cache_file}")

    print("\n4. ETAPA DE CÁLCULO (RUN)")
    # El método run utiliza los datos pre-procesados para rapidez máxima
    matrix = s_index.run()
    
    print("\n5. RESULTADOS (Similitudes)")
    results = s_index.get_result_matrix()
    
    for res in results:
        print(f"Término: {res['term']:<10} | Mejor Voz: {res['best_voice']:<10} | Entidad: {res['entity']:<10} | Calificación: {res['classification']}")
        print(f"  - Scores: {res['scores']}")

    # Limpieza
    for f in [voices_path, citations_path, cache_file]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    demo_workflow()
