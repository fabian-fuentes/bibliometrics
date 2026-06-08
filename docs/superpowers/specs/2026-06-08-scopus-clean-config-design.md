# Diseño: Libreta Scopus consolidada, config segura y salida limpia

**Fecha:** 2026-06-08
**Estado:** Aprobado (diseño)
**Autor:** Fabian Fuentes (con Claude)

## Contexto y problema

El proyecto extrae datos bibliométricos de 21 profesores (TEC-001..TEC-021, ventana
2019–2025) usando el **Scopus Search API** + enriquecimiento con **OpenAlex**.

Estado actual encontrado en el análisis:

1. **Dos libretas divergentes.**
   - `scopus/scopus_publication_level_dataset.ipynb` — la última committeada ("fix key"),
     pero **solo usa Scopus Search API**: `dc:creator` (solo el primer autor) y afiliaciones a
     nivel paper, **sin mapeo autor→afiliación**. No produce los datos que el usuario necesita.
   - `scopus/scopus_publication_level_dataset_OPENALEX.ipynb` — la que **realmente generó el
     output actual** (columnas `paper_authors`, `paper_affiliations`, etc.). Enriquece:
     Scopus Abstract FULL (401 sin acceso institucional) → **OpenAlex por DOI** (gratis).

2. **Token expuesto.** El key `4d64be87…` está hardcodeado como default en la libreta OPENALEX
   (`os.getenv("ELSEVIER_API_KEY", "4d64…")`) y **quedó en el historial de git** (commit `9389abf`).
   Hay remoto en GitHub (`github.com/fabian-fuentes/bibliometrics`) → el key viajó a GitHub.

3. **Mojibake confirmado** en afiliaciones por doble codificación UTF-8:
   `México`→`MÃ©xico`, `Económica`→`EconÃ³mica`, `Investigación`→`InvestigaciÃ³n`.

4. **Exceso de columnas:** 37 en `scopus_publications.csv` + 28 en `scopus_publication_authors.csv`.
   El usuario solo necesita **título, fecha, autores y afiliaciones**.

## Objetivos

- Consolidar en **una sola libreta** (`scopus_publication_level_dataset.ipynb`) basada en la
  lógica OPENALEX, eliminando la duplicada.
- Manejar el token de forma segura vía **`config.py` ignorado por git**, con `config.example.py`
  como plantilla committeada.
- Producir una **base de salida slim, una fila por publicación**, con solo la info necesaria.
- Garantizar **codificación limpia (UTF-8, sin mojibake)** en caracteres especiales.
- **Limpiar el key del historial de git** (con rotación previa del key).

## No-objetivos (YAGNI)

- No se conserva la tabla por-autor (`scopus_publication_authors.csv`) ni `abstract_detail_log.csv`.
- No se agregan métricas nuevas (quartiles, citas, etc.) a la base slim; pueden re-agregarse después.
- No se reescribe el dashboard de Tableau (puede requerir re-mapear columnas; queda fuera de alcance).

## Decisiones (confirmadas con el usuario)

| Decisión | Elección |
|---|---|
| Base de trabajo | Consolidar en una sola libreta (lógica OPENALEX limpia) |
| Forma del output | Una fila por **publicación** |
| Config del token | `config.py` ignorado por git |
| Key en historial | Limpiar el historial (con rotación previa) |
| Dedup multi-profesor | Deduplicar por publicación; profes rastreados como lista en `tracked_prof_ids`/`tracked_prof_names` |
| CSVs extra | Dejar de generar `scopus_publication_authors.csv` y `abstract_detail_log.csv`; mantener `fetch_log.csv` |

## Diseño detallado

### 1. Archivos

- `scopus/config.py` — **(.gitignore)** secretos + parámetros:
  ```python
  ELSEVIER_API_KEY   = "..."        # requerido
  ELSEVIER_INSTTOKEN = None         # opcional (desbloquea Scopus FULL)
  START_YEAR = 2019
  END_YEAR   = 2025
  OUT_DIR    = "scopus_out"
  DATA_DIR   = "data"
  ```
- `scopus/config.example.py` — **(committeado)** misma forma con placeholders y comentarios.
- `.gitignore` — agregar `scopus/config.py` (y `config.py` genérico).
- `scopus/scopus_publication_level_dataset.ipynb` — libreta consolidada (nombre canónico).
- **Eliminar** `scopus/scopus_publication_level_dataset_OPENALEX.ipynb`.

### 2. Carga segura del token

```python
import config
API_KEY    = config.ELSEVIER_API_KEY
INST_TOKEN = getattr(config, "ELSEVIER_INSTTOKEN", None)
assert API_KEY and API_KEY != "PUT-YOUR-KEY-HERE", "Configura tu key en scopus/config.py"
```

### 3. Pipeline

Por cada profesor del roster (21):
1. **Scopus Search** → entradas (papers) con `AU-ID(...) AND PUBYEAR 2019..2025`.
2. **Enriquecer cada paper** vía OpenAlex por DOI
   (`_fetch_openalex_work` + `_parse_author_bundle_from_openalex`, reusados de OPENALEX).
   - Scopus Abstract FULL solo si `INST_TOKEN` presente (off por defecto).
   - Fallback sin DOI: autores/afiliaciones desde Search (`dc:creator`, `affiliation_names`).
3. Construir una fila slim por paper.

### 4. Esquema de salida — `scopus_out/scopus_publications.csv`

Una fila por publicación (deduplicado por `scopus_id`):

| Columna | Origen |
|---|---|
| `tracked_prof_ids` | lista `"; "` de prof_id rastreados que aparecen como autores |
| `tracked_prof_names` | lista `"; "` de nombres de profes rastreados |
| `scopus_id` | `dc:identifier` sin prefijo `SCOPUS_ID:` |
| `doi` | `prism:doi` |
| `title` | `dc:title` |
| `cover_date` | `prism:coverDate` (YYYY-MM-DD) |
| `year` | año derivado de `cover_date` |
| `authors` | nombres ordenados de autores (OpenAlex) unidos con `"; "` |
| `affiliations` | instituciones únicas (OpenAlex) unidas con `"; "` |

Log auxiliar: `scopus_out/fetch_log.csv` (por autor: query, total, capped).

### 5. Codificación

- **Causa raíz:** forzar `response.encoding = "utf-8"` antes de `.json()`/`.text` en llamadas
  a Scopus y OpenAlex.
- **Red de seguridad:** `clean_text(s)` usando **`ftfy.fix_text`** (dependencia nueva) aplicada a
  `title`, `authors`, `affiliations` y cualquier campo de texto.
- **Escritura:** `df.to_csv(..., index=False, encoding="utf-8-sig")` (Excel-friendly; compatible
  con pandas/Tableau).
- **Reparación del CSV existente:** script/celda one-off que abre el `scopus_publications.csv`
  actual, aplica `ftfy.fix_text` a las columnas de texto y reescribe en `utf-8-sig`, para tener
  base limpia inmediata sin re-correr toda la API.

### 6. Limpieza del historial de git (fase final, destructiva)

Prerrequisitos y secuencia:
1. ⚠️ **Rotar el key** en el portal de Elsevier (el key actual ya está en GitHub → comprometido).
2. Actualizar `config.py` local con el key nuevo.
3. Instalar `git-filter-repo` (`pip install git-filter-repo`).
4. Ejecutar replace del string del key en todo el historial (→ `***REMOVED***`), sobre `main`.
5. **`git push --force`** a `origin/main`.

Impacto: reescribe hashes desde la primera aparición; colaboradores deben re-clonar; la rama
feature actual deberá rebasear. Por eso se ejecuta **al final**, idealmente tras mergear el PR
de código, y con confirmación explícita del usuario en el momento.

## Dependencias nuevas

- `ftfy` (reparación de mojibake) — agregar a la celda de instalación.
- `git-filter-repo` (solo para la fase 6).

## Estrategia de verificación

- Dry-run de la libreta con 1–2 autores: `authors` y `affiliations` poblados; `assert "Ã" not in ...`.
- `git check-ignore scopus/config.py` → confirma ignorado.
- `git grep "4d64be87"` en el árbol → sin resultados (tras limpieza).
- Abrir el CSV final: caracteres especiales correctos (`México`, no `MÃ©xico`).

## Riesgos

- **OpenAlex sin DOI:** papers sin DOI no se enriquecen (fallback a Search, autores/afiliaciones
  parciales). ~4 papers en la corrida actual.
- **Reescritura de historial:** operación destructiva con force-push; mitigada ejecutándola al
  final y con rotación previa del key.
- **utf-8-sig BOM:** validado que pandas y Tableau lo manejan; se prefiere por compatibilidad con Excel.
