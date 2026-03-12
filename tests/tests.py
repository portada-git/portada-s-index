# ARCHIVO: test_libreria.py  (en la raíz del proyecto, junto a pyproject.toml)

"""
Prueba básica de portada_s_index.

Ejecutar desde la raíz del proyecto:
    python test_libreria.py

Requisitos previos:
    uv pip install -e .
    o
    pip install -e .
"""

import json
from portada_s_index import SimilarityService
from portada_s_index.data import VoiceList

# =============================================================================
# 1. CONFIGURACIÓN DE ALGORITMOS
# =============================================================================

CONFIG = {
    "version": 2,
    "normalize": True,
    "consensus": {
        "min_votes": 2,
        "require_levenshtein_ocr": True
    },
    "algorithms": {
        "levenshtein_ocr": {
            "enabled": True,
            "threshold": 0.75,
            "gray_zone": [0.71, 0.749],
            "params": {"confusion_cost": 0.4}
        },
        "jaro_winkler": {
            "enabled": True,
            "threshold": 0.85,
            "gray_zone": [0.80, 0.849],
            "params": {"prefix_weight": 0.1}
        },
        "ngram_2": {
            "enabled": True,
            "threshold": 0.63,
            "gray_zone": [0.60, 0.629],
            "params": {"n": 2}
        },
        "ngram_3": {
            "enabled": False,
            "threshold": 0.55,
            "gray_zone": [0.52, 0.549],
            "params": {"n": 3}
        },
        "phonetic_dm": {
            "enabled": False,
            "threshold": 0.85,
            "gray_zone": [0.80, 0.849],
            "params": {}
        },
        "semantica": {
            "enabled": True,
            "threshold": 0.72,
            "gray_zone": [0.65, 0.719],
            "params": {"mode": "token_jaccard"}
        },
        "text2vec": {
            "enabled": True,
            "threshold": 0.78,
            "gray_zone": [0.72, 0.779],
            "params": {"mode": "char_cosine", "n": 3}
        },
    }
}

# =============================================================================
# 2. VOCES CONOCIDAS (tú las pasas desde donde las tengas)
# =============================================================================

VOICES = {
    "BERGANTIN": [
        "bergantín", "bgn", "berg.", "brigantine",
        "bg.", "ber.", "brg.", "brick", "brig", "br"
    ],
    "BERGANTIN-GOLETA": [
        "bergantín-goleta", "bergantín goleta", "bn goleta",
        "b.n-goleta", "brick-goélette", "br.-g", "br-goel"
    ],
    "BOMBARDA": [
        "bombarda", "bombarde", "bom", "bomb"
    ],
    "BALANDRA": [
        "balandra", "balandro", "bal.a", "bal.o",
        "bal.", "baland.", "balandre"
    ],
    "BARCA": [
        "barca", "barke", "bk.", "bark",
        "bca.", "barque", "bk"
    ],
}

# =============================================================================
# 3. TÉRMINOS A EVALUAR (los que tienes en tu CSV o base de datos)
# =============================================================================

TERMS = [
    # Exactos — deben dar EXACT
    {"term": "brig",      "frequency": 34},
    {"term": "bom",       "frequency": 45},
    {"term": "bgn",       "frequency": 12},
    {"term": "bark",      "frequency": 88},

    # Con ruido OCR — deben dar CONSENSUS
    {"term": "bergt",     "frequency": 8},
    {"term": "brigt",     "frequency": 5},
    {"term": "balandra",  "frequency": 21},
    {"term": "bomba",     "frequency": 3},

    # Zona gris — deben dar GRAY_ZONE o WEAK
    {"term": "barca.",    "frequency": 2},
    {"term": "brg",       "frequency": 7},

    # Sin coincidencia — deben dar REJECTED
    {"term": "xyz99",     "frequency": 1},
    {"term": "aaaa",      "frequency": 1},
]

# =============================================================================
# 4. EJECUTAR
# =============================================================================

def main():
    print("=" * 60)
    print("TEST portada_s_index")
    print("=" * 60)

    # Construir VoiceList desde dict (tú decides cómo cargar las voces)
    voice_list = VoiceList.from_dict("ship_type", VOICES)
    print(f"\nVoices cargadas: {len(voice_list)} variantes, {len(voice_list.entities)} entidades")
    print(f"Entidades: {voice_list.entities}")

    # Crear servicio desde config dict
    service = SimilarityService.from_dict(CONFIG)
    print(f"\nAlgoritmos activos: {service.active_algorithms}")

    # Evaluar
    print(f"\nEvaluando {len(TERMS)} términos...")
    results = service.evaluate(TERMS, voice_list)

    # Mostrar resumen
    print("\n" + "=" * 60)
    print(f"{'TÉRMINO':<15} {'CLASIFICACIÓN':<18} {'ENTIDAD':<22} {'VOTOS'}")
    print("-" * 60)

    counts = {}
    for r in results:
        clf = r["classification"]
        counts[clf] = counts.get(clf, 0) + 1
        print(
            f"{r['term']:<15} "
            f"{clf:<18} "
            f"{r['entity'] or '—':<22} "
            f"{r['votes']}"
        )

    # Resumen por clasificación
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("-" * 60)
    for clf, n in sorted(counts.items()):
        print(f"  {clf:<18}: {n}")

    # JSON completo del primer resultado no-EXACT para ver el debug
    print("\n" + "=" * 60)
    print("DEBUG COMPLETO — primer término no exacto:")
    print("-" * 60)
    for r in results:
        if not r["exact_match"]:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            break


if __name__ == "__main__":
    main()