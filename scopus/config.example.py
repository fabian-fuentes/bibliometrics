"""Plantilla de configuración para la libreta de Scopus.

Copia este archivo a `config.py` y coloca tu key real:

    cp config.example.py config.py

`config.py` está en .gitignore — tu key NUNCA se versiona en git.
"""

# ── Credenciales (requerido) ─────────────────────────────────────────────────
# Tu API key de Elsevier/Scopus. Consíguela en https://dev.elsevier.com/
ELSEVIER_API_KEY = "PUT-YOUR-KEY-HERE"

# Token institucional (opcional). Si lo tienes, desbloquea la vista FULL del
# Abstract API (autores/afiliaciones nativos de Scopus). Déjalo en None si no.
ELSEVIER_INSTTOKEN = None

# ── Parámetros de extracción ─────────────────────────────────────────────────
START_YEAR = 2019   # año inicial (inclusivo)
END_YEAR   = 2025   # año final (inclusivo)

OUT_DIR = "scopus_out"  # carpeta de salida (relativa a scopus/)
DATA_DIR = "data"       # carpeta de insumos (quartiles, etc.)
