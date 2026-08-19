<div align="center">

# MiArchivos

**Entendé qué ocupa espacio y cómo está organizado, sin subir tus archivos.**

[![CI](https://github.com/amoedo7/MiArchivos/actions/workflows/ci.yml/badge.svg)](https://github.com/amoedo7/MiArchivos/actions/workflows/ci.yml)

`Android / Termux` · `Windows` · `macOS` · `Linux` · `SHA-256` · `JSON`
</div>

---

## Qué hace

MiArchivos analiza una carpeta local en modo lectura y resume:

- cantidad de archivos y carpetas;
- tamaño total;
- extensiones predominantes;
- archivos más grandes;
- errores de lectura encontrados;
- duplicados por SHA-256 **sólo si se pide explícitamente**.

No borra, mueve, renombra ni sube archivos.

## Ejecutar

```bash
python miarchivos.py .
```

Analizar Descargas:

```bash
python miarchivos.py ~/downloads --output archivos.json
```

Buscar duplicados:

```bash
python miarchivos.py ~/downloads --duplicates
```

Limitar el recorrido:

```bash
python miarchivos.py . --max-files 10000 --top 20
```

## Contrato

```json
{
  "schema": "desarrollamo.miarchivos.v1",
  "summary": {
    "files": 421,
    "directories": 31,
    "total_bytes": 2147483648
  },
  "largest_files": [],
  "extensions": {},
  "duplicates": {"enabled": false}
}
```

El hashing de duplicados puede tardar y leer una gran cantidad de datos, por eso está desactivado por defecto.

---

**DesarrollAMO** · análisis local primero; acciones destructivas, nunca por sorpresa.
