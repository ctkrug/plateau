// Loads the plateau/ Python package (copied into vendor/ by scripts/build_site.py)
// into a Pyodide runtime so it can be imported like a normal package.

async function loadPlateauPackage() {
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
  });

  const manifestResponse = await fetch("vendor/manifest.json");
  if (!manifestResponse.ok) {
    throw new Error(`could not load vendor/manifest.json (${manifestResponse.status})`);
  }
  const manifest = await manifestResponse.json();

  const pkgRoot = "/plateau_pkg/plateau";
  pyodide.FS.mkdirTree(pkgRoot);

  for (const relPath of manifest) {
    const source = await (await fetch(`vendor/plateau/${relPath}`)).text();
    const parts = relPath.split("/");
    const fileName = parts.pop();
    let dir = pkgRoot;
    for (const part of parts) {
      dir += `/${part}`;
      pyodide.FS.mkdirTree(dir);
    }
    pyodide.FS.writeFile(`${dir}/${fileName}`, source);
  }

  pyodide.runPython("import sys; sys.path.insert(0, '/plateau_pkg')");
  return pyodide;
}
