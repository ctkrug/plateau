# site/

The static, self-contained page published to `apps.charliekrug.com/plateau`. All asset paths
are relative so it works under any base path.

`vendor/` (generated, gitignored) holds a copy of the `plateau/` Python package plus a
manifest — `js/pyodide-loader.js` fetches those files at runtime and writes them into
Pyodide's virtual filesystem so `import plateau` works in the browser exactly as it does under
pytest. Regenerate it before serving or deploying:

```
python3 scripts/build_site.py   # or: make build-site
```

## Local development

```
make serve
```

Serves `site/` at `http://localhost:8000`. A plain `file://` open won't work — most browsers
block the `fetch()` calls Pyodide and the loader rely on under that scheme.
