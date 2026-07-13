# Inventory API — Mini-proyecto de Integración Continua

API REST de gestión de inventario hecha con Flask para el mini-proyecto de CI. Incluye la suite de pruebas, análisis estático y el pipeline de GitHub Actions.

## Estructura

```
├── src/                  # Código fuente (modelo, repositorio, servicio, rutas, app)
├── tests/
│   ├── unit/             # Tests unitarios de la lógica de negocio (49 tests)
│   └── integration/      # Tests de integración de endpoints HTTP (21 tests)
├── config/               # Configuración por entorno
├── docs/                 # Guía de setup y guion del video
├── .github/workflows/    # Pipeline CI (ci.yml)
├── htmlcov/              # Reporte HTML de cobertura (evidencia)
└── CI_REPORT.md          # Documentación del pipeline y métricas
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/api/products` | Listar productos |
| POST | `/api/products` | Crear producto |
| GET | `/api/products/<id>` | Obtener producto |
| PUT | `/api/products/<id>` | Actualizar producto (parcial) |
| DELETE | `/api/products/<id>` | Eliminar producto |
| PATCH | `/api/products/<id>/stock` | Ajustar stock (`{"delta": -3}`) |
| GET | `/api/products/low-stock?threshold=N` | Productos con stock bajo |

Ejemplo:

```bash
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Arroz 5lb", "price": 4.50, "stock": 20, "category": "granos"}'
```

Para probar la API completa desde Postman, importa `Inventory-API.postman_collection.json` (raíz del repo): trae el flujo CRUD encadenado, los endpoints de stock, los casos de error y tests de aserción en cada request. Las instrucciones de uso están en la descripción de la propia colección.

## Seguridad básica

Si se define la variable de entorno `API_KEY`, todas las operaciones de escritura (POST/PUT/PATCH/DELETE) exigen la cabecera `X-API-Key`. Además, todas las respuestas incluyen cabeceras `X-Content-Type-Options: nosniff` y `X-Frame-Options: DENY`.

## Ejecución local

Usa [uv](https://docs.astral.sh/uv/) para gestionar dependencias (la fuente de verdad es `pyproject.toml` + `uv.lock`).

```bash
# instalar uv si no lo tienes:
curl -LsSf https://astral.sh/uv/install.sh | sh    # Windows: irm https://astral.sh/uv/install.ps1 | iex

uv sync                                            # crea .venv e instala todo desde el lock
uv run python -m src.app                           # levanta en http://127.0.0.1:5000
```

Si prefieres pip, `requirements.txt` se mantiene por compatibilidad: `pip install -r requirements.txt`.

## Tests y calidad

```bash
uv run pytest                                             # toda la suite
uv run pytest tests/unit -v                               # solo unitarios
uv run pytest --cov --cov-report=html --cov-fail-under=80 # cobertura + reporte en htmlcov/
uv run pylint src config --fail-under=9.5                 # análisis estático
```

## CI/CD

Cada push a `main` ejecuta el pipeline de GitHub Actions con 6 stages: install → lint → test → coverage → sonarcloud + build.
