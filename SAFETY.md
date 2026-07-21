# Safety and security model

- SkyFoundry output is a creative concept simulation, never professional advice.
- Model and external payloads are rejected unless they match strict schemas; extra fields are forbidden.
- Agents can submit only allowlisted, versioned Building DSL operations. There is no `eval`, generated JSX, shader source, arbitrary HTML, URL retrieval, or filesystem path in the scene write path.
- Action, component, string, array, worker, instance, material, and project budgets are capped.
- Browser text is rendered through React text nodes; it is not injected as HTML.
- Live model calls require explicit credentials and remain disabled by default. Provider outputs are parsed again before use.
- The CAD adapter accepts bounded dimensional recipes. It does not execute model-generated Python or install CadQuery in the base environment. Its optional child uses a temporary directory, socket denial, a 20-second timeout, and CPU, address-space, file-size, and open-file limits before copying validated artifacts out.
- TRELLIS, external GLB ingestion, live OSM, and raw CadQuery are disabled by default.
- SQLite project IDs are bound parameters. Large snapshots belong in the configured artifact directory.

The implementation does not claim structural safety, code compliance, constructability, cost accuracy, zoning validity, or geotechnical validity.
