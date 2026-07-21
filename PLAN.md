# PLAN.md — SkyFoundry

## 0. Product goal

Build **SkyFoundry**, a browser-based, agentic 3D construction sandbox in which a user describes a site and a skyscraper concept in natural language, then watches a team of AI agents collaboratively design and visually construct the building.

The result is an **interactive architectural concept simulator**, not professional architecture, structural engineering, permitting software, construction planning, or a physically accurate digital twin.

A successful MVP must feel like this:

1. The user opens a cinematic, pannable, zoomable 3D city block.
2. The user enters a prompt such as:

   > Build a 32-storey mixed-use glass tower on this empty Manhattan lot. Use a stone podium, a tapered crown, warm interior lighting, a public plaza, and a rooftop garden.

3. A small team of named agents discusses the brief.
4. Agents propose fine-grained scene actions through a typed building DSL:
   - create grid;
   - excavate;
   - add foundation mat;
   - place core;
   - place columns;
   - connect beams;
   - add slabs;
   - install curtain-wall panels;
   - add lobby canopy;
   - place a tower crane;
   - add temporary scaffolding;
   - stage materials;
   - add workers and vehicles;
   - animate each construction task.
5. The system validates those actions before execution.
6. The browser animates the building being assembled over time.
7. The user can pause, orbit, scrub the construction timeline, select any component, inspect which agent created it, and ask for a revision.
8. The final concept can be exported as:
   - project JSON;
   - scene JSON;
   - construction timeline JSON;
   - screenshot;
   - GLB where practical.

The MVP must work without a GPU, without paid APIs, and without external service credentials by using deterministic scripted agents and a procedural asset factory. Multimodal model calls, CadQuery, OSM context, and generative 3D services are adapters layered on top, not critical-path dependencies.

---

# 1. Product boundaries

## 1.1 What SkyFoundry is

SkyFoundry is:

- a creative simulation;
- an agent collaboration demo;
- a procedural 3D building generator;
- a construction-sequence visualizer;
- a visual explanation of how building components fit together;
- a testbed for multimodal agents that inspect screenshots and issue constrained scene operations;
- a browser experience first.

## 1.2 What SkyFoundry is not

Do not present any output as:

- structurally safe;
- code compliant;
- permit ready;
- constructible;
- cost accurate;
- geotechnically valid;
- compliant with zoning or air-rights rules;
- an accurate representation of an actual parcel;
- professional architectural or engineering advice.

Show a persistent but unobtrusive notice:

> Conceptual simulation only. Not architectural, structural, construction, zoning, or safety advice.

## 1.3 Scope discipline

The first release must prioritize a compelling, reliable construction loop over open-ended realism.

The critical path is:

```text
prompt
→ structured brief
→ typed actions
→ validation
→ procedural asset generation
→ animated scene mutation
→ screenshots
→ next agent round
```

The following must remain optional:

- arbitrary real-world site retrieval;
- photorealistic New York geometry;
- neural text-to-3D generation;
- unrestricted LLM-generated CadQuery code;
- accurate structural simulation;
- detailed worker AI;
- real-time multiplayer;
- BIM export;
- live construction scheduling data.

---

# 2. MVP definition

## 2.1 Required MVP demo

The repository must ship with a complete local demo named:

**Manhattan Tower Demo**

The demo contains:

- a stylized downtown Manhattan-like block;
- one empty buildable lot;
- surrounding extruded buildings;
- roads, sidewalks, street trees, streetlights, and simple traffic;
- an orbitable and zoomable camera;
- day/night lighting controls;
- a default prompt for a 24–32-storey tower;
- at least six visible agent rounds;
- at least eight construction phases;
- at least 400 individually addressable logical components;
- efficient instancing so the browser remains responsive;
- animated assembly;
- a construction timeline;
- an agent activity panel;
- a component inspector;
- deterministic replay.

## 2.2 Required construction phases

The default build must visibly progress through:

1. Site setup
2. Excavation
3. Foundation
4. Core
5. Primary structure
6. Floor slabs
7. Façade
8. Roof and crown
9. Public realm
10. Completion

At minimum, the browser must animate:

- excavation depth changing;
- piles or foundation elements appearing;
- the concrete core rising;
- columns being placed floor by floor;
- beams connecting;
- slabs being added;
- curtain-wall panels attaching;
- a crane growing and moving loads;
- temporary scaffolding appearing and disappearing;
- workers or equipment moving through simple scripted paths;
- final lighting turning on.

## 2.3 Required interaction

The user can:

- enter or edit the building brief;
- start a design/build run;
- pause and resume;
- orbit, pan, zoom, and reset the camera;
- switch between overview, street, crane, section, and top views;
- scrub the timeline;
- select a component;
- hide/show systems;
- inspect agent proposals and validation results;
- approve or reject a proposed revision;
- request one scoped revision in natural language;
- replay the full build;
- export the project.

---

# 3. Design philosophy

## 3.1 Declarative scene first

Agents do not write arbitrary Three.js code.

Agents emit a strict JSON action language. The application owns all rendering, physics, asset generation, animation, IDs, transforms, materials, performance constraints, and undo/redo.

## 3.2 Deterministic geometry first

Structural-looking elements must be generated procedurally from dimensions and parameters.

Use neural 3D generation only for decorative props where topology and dimensions are not mission-critical.

Examples suitable for optional neural asset generation:

- lobby sculpture;
- planter;
- unusual bench;
- abstract art;
- decorative roof feature;
- construction-site prop;
- furniture.

Examples that must remain procedural:

- grids;
- cores;
- columns;
- beams;
- slabs;
- façade panels;
- stairs;
- braces;
- foundations;
- cranes used by the simulator;
- safety rails;
- scaffolding;
- floors;
- walls.

## 3.3 Physics as visual plausibility

Use a rigid-body engine for:

- collision;
- object settling;
- crane-load swing;
- falling debris in sandbox mode;
- equipment contact;
- simple worker navigation blockers.

Do not use the physics engine as proof of structural integrity.

Structural validation in the MVP is a deterministic **geometric plausibility layer**, not finite-element analysis.

## 3.4 Multimodal agent loop

Each visual agent round receives:

- the current structured project state;
- a compact scene summary;
- construction phase;
- outstanding goals;
- recent action history;
- budget remaining;
- one to four screenshots from canonical cameras;
- validation warnings;
- the user brief.

The model returns only schema-valid proposals.

---

# 4. User experience

## 4.1 Landing screen

Show:

- product title;
- one large brief input;
- three example prompts;
- scene preset selector;
- style chips;
- height/floor range;
- simulation speed;
- “Start design session.”

Scene presets:

- Manhattan block
- Generic downtown block
- Waterfront lot
- Empty sandbox

Only Manhattan block and Empty sandbox must be fully implemented in MVP. Other presets may be disabled with “coming later.”

## 4.2 Main studio layout

Desktop:

```text
┌────────────────────────────────────────────────────────────────────┐
│ Project name | phase | simulation controls | view controls        │
├──────────────────┬────────────────────────────────┬────────────────┤
│                  │                                │                │
│ Design brief     │                                │ Agent studio   │
│ Constraints      │       3D construction scene    │ proposals      │
│ System toggles   │                                │ critiques      │
│ Component tree   │                                │ validation     │
│                  │                                │                │
├──────────────────┴────────────────────────────────┴────────────────┤
│ Construction timeline, phase markers, scrubber                    │
└────────────────────────────────────────────────────────────────────┘
```

On narrower screens:

- scene remains primary;
- side panels become drawers;
- timeline remains docked;
- touch orbit controls work;
- no guarantee of full mobile authoring, but viewing and playback must work.

## 4.3 Agent studio

Display agents as a working architecture studio:

- Lead Architect
- Structural Concept Agent
- Façade Designer
- Construction Planner
- Site Logistics Agent
- Visual Critic
- Build Controller

For every round, show:

- agent name;
- concise reasoning summary;
- proposed actions;
- action count;
- validation results;
- accepted/rejected status;
- screenshot used;
- elapsed time.

Do not expose hidden chain of thought. Show concise, purpose-written rationale fields from the structured response.

## 4.4 Component inspector

Selecting a component displays:

- component ID;
- type;
- level;
- dimensions;
- position;
- material;
- parent;
- dependencies;
- construction task;
- created by;
- creation round;
- current state;
- warnings;
- show/hide;
- focus camera;
- delete in sandbox mode;
- request revision.

## 4.5 Revision interaction

Example:

> Make the podium three floors taller and replace the ground-floor glass with stone arches.

The system should:

1. parse the revision;
2. identify affected components;
3. produce a scoped change set;
4. preview deletions and additions;
5. validate;
6. animate demolition/replacement;
7. preserve unaffected IDs where possible.

---

# 5. Technical architecture

## 5.1 Stack

Use a monorepo.

### Browser

- Next.js
- React
- TypeScript
- React Three Fiber
- Drei
- Three.js
- `@react-three/rapier`
- Zustand
- Framer Motion for non-canvas UI
- Tailwind CSS
- Radix or another accessible headless component set
- Zod
- Playwright
- Vitest

### Orchestrator

- Python 3.11+
- FastAPI
- LangGraph
- Pydantic
- SQLite for MVP persistence
- filesystem artifact store
- WebSocket or Server-Sent Events for run streaming
- provider adapters for multimodal model APIs

### CAD worker

- Python
- CadQuery
- isolated subprocess execution
- STEP/STL generation
- mesh conversion to GLB where available
- strict time, memory, import, and output limits

### Optional asset-generation worker

Provider interface only:

- local TRELLIS-compatible worker;
- remote user-supplied endpoint;
- mock provider.

The MVP must not install TRELLIS by default.

## 5.2 Repository layout

```text
skyfoundry/
├── PLAN.md
├── AGENTS.md
├── PROGRESS.md
├── README.md
├── ARCHITECTURE.md
├── SAFETY.md
├── LICENSE_NOTES.md
├── .env.example
├── package.json
├── pnpm-workspace.yaml
├── docker-compose.yml
├── apps/
│   ├── web/
│   ├── orchestrator/
│   └── cad-worker/
├── packages/
│   ├── scene-schema/
│   ├── building-dsl/
│   ├── procedural-assets/
│   ├── construction-engine/
│   ├── scene-runtime/
│   ├── scene-validation/
│   ├── agent-prompts/
│   ├── agent-client/
│   ├── osm-importer/
│   ├── fixture-projects/
│   └── test-utils/
├── assets/
│   ├── textures/
│   ├── hdris/
│   ├── icons/
│   └── fixtures/
├── artifacts/
│   └── .gitkeep
├── scripts/
│   ├── seed-demo.ts
│   ├── validate-project.ts
│   ├── render-project.ts
│   └── export-glb.ts
└── tests/
    ├── contract/
    ├── integration/
    ├── e2e/
    └── visual/
```

## 5.3 Development commands

Implement:

```bash
pnpm install
pnpm dev
pnpm build
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
pnpm test:visual
pnpm demo:seed
pnpm demo:run
pnpm validate:project
```

The local fixture experience must work with one top-level command after installation.

---

# 6. Coordinate system and scene rules

## 6.1 Units

- One world unit equals one meter.
- Y is vertical.
- X and Z define the ground plane.
- All component dimensions use meters.
- Store rotations in degrees in API payloads and convert internally.
- Use local project coordinates.
- Real-world longitude/latitude is optional metadata, never the renderer’s primary coordinate system.

## 6.2 Lot

```ts
type LotSpec = {
  id: string;
  polygon: Array<[number, number]>;
  elevation: number;
  setbacks: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  maxConceptHeight?: number;
};
```

The Manhattan fixture must use a rectangular lot, but the schema must allow polygons.

## 6.3 Level system

```ts
type Level = {
  id: string;
  index: number;
  name: string;
  elevation: number;
  floorToFloorHeight: number;
  use: "lobby" | "retail" | "office" | "residential" | "mechanical" | "amenity" | "roof";
};
```

## 6.4 Stable IDs

Every logical component receives a stable ID.

Examples:

```text
tower-a/core/main
tower-a/level/012/slab/main
tower-a/level/012/column/grid-c4
tower-a/level/012/beam/c4-d4
tower-a/level/012/facade/north/panel/008
site/crane/tower-01
```

IDs must remain stable across deterministic replay.

---

# 7. Building DSL

## 7.1 Core principle

The Building DSL is the only write interface available to agents.

The DSL must be:

- typed;
- JSON serializable;
- schema versioned;
- validated;
- replayable;
- reversible where practical;
- deterministic;
- auditable.

## 7.2 Action envelope

```ts
type SceneAction = {
  id: string;
  schemaVersion: "1.0";
  roundId: string;
  agentId: string;
  timestamp: string;
  operation: SceneOperation;
  rationale: string;
  goalIds: string[];
  dependsOn: string[];
  confidence: number;
  estimatedComponentCount: number;
};
```

## 7.3 Required operations

```ts
type SceneOperation =
  | CreateProjectOperation
  | DefineLotOperation
  | DefineGridOperation
  | DefineLevelsOperation
  | AddComponentOperation
  | AddComponentArrayOperation
  | UpdateComponentOperation
  | RemoveComponentOperation
  | AttachComponentOperation
  | GroupComponentsOperation
  | AddMaterialOperation
  | AssignMaterialOperation
  | AddConstructionTaskOperation
  | AddAnimationOperation
  | AddCameraCueOperation
  | AddWorkerPathOperation
  | AddVehiclePathOperation
  | SetPhaseOperation
  | AddNoteOperation;
```

## 7.4 Component types

Required procedural component vocabulary:

### Site

- lot
- excavation
- soil_volume
- street
- sidewalk
- curb
- fence
- gate
- temporary_office
- material_stack
- dumpster
- streetlight
- tree
- planter
- bench

### Substructure

- pile
- pile_cap
- footing
- foundation_mat
- basement_wall
- retaining_wall
- grade_beam

### Superstructure

- core
- core_segment
- column
- mega_column
- beam
- transfer_beam
- brace
- outrigger
- belt_truss
- slab
- slab_opening
- stair
- ramp

### Envelope

- exterior_wall
- curtain_wall_system
- curtain_wall_panel
- mullion
- spandrel
- window
- door
- canopy
- louver
- parapet
- crown
- roof_screen

### Interiors and systems

MVP uses simplified visual placeholders:

- partition
- elevator_shaft
- elevator_car
- mechanical_zone
- riser
- ceiling
- light_fixture

### Construction equipment

- tower_crane
- mobile_crane
- hoist
- scaffold
- safety_rail
- excavator
- concrete_truck
- flatbed_truck
- forklift
- worker
- load

## 7.5 Add component

```ts
type AddComponentOperation = {
  kind: "add_component";
  component: {
    id: string;
    type: ComponentType;
    parentId?: string;
    levelId?: string;
    generator: string;
    parameters: Record<string, unknown>;
    transform: {
      position: [number, number, number];
      rotation: [number, number, number];
      scale: [number, number, number];
    };
    materialId?: string;
    tags: string[];
    metadata: Record<string, unknown>;
  };
};
```

## 7.6 Add array

Agents should use array actions rather than issuing hundreds of repeated calls.

```ts
type AddComponentArrayOperation = {
  kind: "add_component_array";
  idPattern: string;
  componentType: ComponentType;
  generator: string;
  baseParameters: Record<string, unknown>;
  placements:
    | { mode: "grid"; rows: number; columns: number; spacingX: number; spacingZ: number }
    | { mode: "levels"; levelIds: string[]; localTransform: Transform }
    | { mode: "polyline"; points: Array<[number, number, number]>; spacing: number }
    | { mode: "explicit"; transforms: Transform[] };
  materialId?: string;
  tags: string[];
};
```

## 7.7 Agent action limits

Per agent, per round:

- maximum 12 action envelopes;
- maximum 2,000 generated logical components;
- maximum 50,000 rendered instances in the entire project;
- maximum one destructive operation group;
- no arbitrary executable code;
- no direct URL retrieval;
- no filesystem paths;
- no shader source.

---

# 8. Procedural asset factory

## 8.1 Factory interface

```ts
interface ProceduralGenerator<TParams> {
  id: string;
  schema: ZodSchema<TParams>;
  estimate(params: TParams): AssetEstimate;
  generate(params: TParams, context: GeneratorContext): GeneratedAsset;
}
```

## 8.2 Required generators

Implement deterministic generators for:

- box
- cylinder
- extruded_polygon
- slab
- rectangular_column
- circular_column
- steel_i_beam
- rectangular_beam
- brace
- concrete_core
- stair_flight
- curtain_wall_panel
- mullion_grid
- punched_window_wall
- stone_arch_bay
- canopy
- parapet
- crown
- tower_crane
- scaffold_bay
- safety_rail
- pile
- foundation_mat
- excavation_volume
- worker_capsule
- excavator_proxy
- truck_proxy
- tree_proxy
- streetlight_proxy

These need not be manufacturing-grade meshes. They must be visually clean, dimensionally consistent, and efficient.

## 8.3 Instancing

Use instanced meshes for repeated assets:

- columns;
- façade panels;
- mullions;
- workers;
- safety rails;
- trees;
- lights.

Maintain a logical component registry mapping component IDs to instance indices.

Selection must still work.

## 8.4 Materials

Required material presets:

- cast concrete
- polished concrete
- dark steel
- galvanized steel
- clear glass
- blue glass
- low-iron glass
- stone
- brick
- wood
- aluminum
- safety orange
- soil
- asphalt
- vegetation
- emissive interior

Materials are stylized PBR approximations.

## 8.5 LOD

Implement at least two levels of detail for:

- surrounding buildings;
- façade systems;
- workers;
- vehicles;
- cranes.

At distance, render façade panels as merged or instanced surfaces.

---

# 9. CAD generation adapter

## 9.1 Role

CadQuery is optional and intended for bounded, dimension-driven custom parts.

Examples:

- custom column capital;
- custom connection plate;
- decorative canopy bracket;
- façade clip prototype;
- planter profile;
- custom bench.

Do not route primary tower generation through CadQuery.

## 9.2 Safety

Never execute unrestricted model-generated Python in the main process.

The CAD worker must:

- run in an isolated subprocess or container;
- prohibit network access;
- apply a module allowlist;
- apply wall-clock timeout;
- apply memory limit where supported;
- cap output file size;
- write only to a temporary job directory;
- scan source for disallowed imports and calls;
- terminate on validation failure;
- return structured logs.

## 9.3 Preferred CAD request format

Do not ask the model to write Python first.

Ask it to emit a constrained CAD recipe:

```json
{
  "primitive": "extruded_profile",
  "units": "m",
  "profile": {
    "type": "rounded_rectangle",
    "width": 1.2,
    "depth": 0.6,
    "radius": 0.08
  },
  "height": 0.25,
  "holes": [],
  "fillets": [
    {"edgeSelector": "vertical", "radius": 0.02}
  ]
}
```

Translate recipes to CadQuery with trusted templates.

Add a developer-only escape hatch for raw CadQuery scripts, disabled by default.

## 9.4 CQAsk relationship

Treat `OpenOrion/CQAsk` as inspiration and an optional experiment, not a production dependency.

Its public implementation demonstrates natural-language-to-CadQuery generation and exports CAD files, but the MVP must replace unrestricted generated code with the constrained recipe and sandbox described here.

Reference:

- https://github.com/OpenOrion/CQAsk
- https://github.com/CadQuery/cadquery

---

# 10. Generative 3D adapter

## 10.1 Role

Generative 3D is optional and asynchronous.

Use it for decorative, non-structural assets only.

## 10.2 Interface

```py
class AssetGenerationProvider(Protocol):
    async def generate(self, request: AssetGenerationRequest) -> AssetGenerationResult:
        ...
```

```py
class AssetGenerationRequest(BaseModel):
    prompt: str
    reference_image_paths: list[str] = []
    category: Literal[
        "sculpture",
        "furniture",
        "landscape_prop",
        "construction_prop",
        "decorative_roof_feature"
    ]
    target_size_m: tuple[float, float, float]
    triangle_budget: int
    seed: int
```

## 10.3 Required providers

- `MockAssetGenerationProvider`
- `LocalFolderAssetProvider`
- `TrellisProvider` interface and documented setup, disabled by default

## 10.4 TRELLIS constraints

Do not make the base repository install or run TRELLIS automatically.

Document that TRELLIS:

- is a separate GPU-heavy service;
- is best treated as image-conditioned asset generation;
- can export mesh/GLB output;
- should be isolated from the web/orchestrator process;
- requires post-processing and polygon reduction before browser use.

References:

- https://github.com/microsoft/TRELLIS
- https://microsoft.github.io/TRELLIS/

The app must remain fully useful when `ENABLE_TRELLIS=false`.

---

# 11. Construction engine

## 11.1 Construction task model

```ts
type ConstructionTask = {
  id: string;
  name: string;
  phase: ConstructionPhase;
  componentIds: string[];
  predecessorIds: string[];
  startTick: number;
  durationTicks: number;
  crewType?: string;
  equipmentIds: string[];
  animationPreset: string;
  status: "planned" | "ready" | "active" | "complete" | "blocked";
};
```

## 11.2 Phase DAG

Use a dependency graph.

Example:

```text
site fence
→ excavation
→ piles
→ foundation mat
→ core level 1
→ columns level 1
→ beams level 1
→ slab level 1
→ core level 2
...
→ façade starts after configurable structural lead
→ crown
→ public realm
```

## 11.3 Animation presets

Required:

- `fade_and_scale`
- `lift_and_place`
- `crane_pick_and_place`
- `rise_from_ground`
- `concrete_pour`
- `extrude_upward`
- `panel_attach`
- `roll_in_vehicle`
- `worker_walk`
- `excavate`
- `demolish`
- `scaffold_assemble`
- `lights_power_on`

## 11.4 Crane simulation

The tower crane is a visual system with:

- mast sections;
- jib;
- counter-jib;
- trolley;
- hook;
- cable;
- load;
- slew rotation;
- trolley travel;
- lift height.

Use deterministic keyframed motion. Use Rapier only to add subtle load swing and collision guards.

The crane must not calculate real lift plans.

## 11.5 Worker simulation

Workers may be stylized capsules or low-poly figures.

MVP behavior:

- follow waypoints;
- idle;
- carry a small prop;
- gather near active work;
- avoid obvious obstacles;
- never require autonomous crowd simulation.

Use no more than 30 active workers.

## 11.6 Construction speed

Simulation time is fictional.

Provide:

- 0.25×
- 1×
- 4×
- 16×
- instant phase

---

# 12. Geometric plausibility validation

## 12.1 Validation pipeline

Every action batch passes:

1. Schema validation
2. Permission validation
3. ID validation
4. Project-bound validation
5. Parameter validation
6. Lot-bound validation
7. Collision validation
8. Support validation
9. Level consistency
10. Dependency validation
11. Performance budget validation
12. Construction-phase validation

## 12.2 Support graph

Build a simplified support graph.

Rules:

- slabs require overlap with core, columns, or supporting walls;
- beams require two supports;
- columns above level 0 require a supporting component below within tolerance;
- façade panels require a slab edge, wall, or façade parent;
- crown elements require roof support;
- crane requires foundation or base;
- floating components fail validation unless tagged `decorative_suspended`.

This is not engineering analysis.

## 12.3 Collision policy

Classify collisions:

- expected overlap;
- tolerated;
- warning;
- error.

Examples:

- beam into column: expected;
- window panel into slab edge: warning or expected by tolerance;
- worker inside core wall: error;
- crane mast through tower: error;
- two columns occupying same grid point: error.

## 12.4 Budget validation

Default budgets:

```text
logical components: 20,000
rendered instances: 50,000
unique geometries: 250
unique materials: 80
active rigid bodies: 150
active workers: 30
active vehicles: 10
agent rounds: 20
screenshots per round: 4
```

---

# 13. Agent system

## 13.1 LangGraph state

```py
class ProjectState(BaseModel):
    project_id: str
    user_brief: str
    brief: BuildingBrief | None
    scene_summary: SceneSummary
    current_phase: str
    goals: list[DesignGoal]
    unresolved_issues: list[Issue]
    proposed_actions: list[SceneAction]
    accepted_actions: list[SceneAction]
    rejected_actions: list[RejectedAction]
    construction_tasks: list[ConstructionTask]
    screenshots: list[SceneScreenshot]
    round_index: int
    budgets: BudgetState
    status: Literal[
        "briefing",
        "concept",
        "planning",
        "building",
        "review",
        "revision",
        "complete",
        "failed"
    ]
```

## 13.2 Graph

```text
START
  |
  v
Brief Interpreter
  |
  v
Lead Architect
  |
  +------------------------------+
  |              |               |
  v              v               v
Structural    Façade          Site Logistics
Concept       Designer        Agent
  |              |               |
  +--------------+---------------+
                 |
                 v
Construction Planner
                 |
                 v
Action Validator
        | accepted      | rejected
        v               v
Build Controller     Revision Router
        |
        v
Render Canonical Views
        |
        v
Visual Critic
        |
        +---- more work? ---- yes ----> Lead Architect
        |
        no
        v
Final Review
        |
        v
END
```

## 13.3 Human-in-the-loop

Human approval is optional during the first concept run and required for:

- destructive revisions affecting more than 15% of components;
- changing project height by more than 20%;
- deleting the core;
- replacing the façade system globally;
- importing an external generated asset;
- running raw CAD developer mode.

## 13.4 Deterministic mode

Implement a full scripted agent provider.

It must produce the same Manhattan tower from a seed and exercise the same LangGraph nodes without model calls.

Environment:

```bash
AGENT_PROVIDER=scripted
```

This mode is required for tests and the default first-run experience.

## 13.5 Multimodal model adapter

Provide a generic interface:

```py
class MultimodalAgentProvider(Protocol):
    async def propose(
        self,
        system_prompt: str,
        state_payload: dict,
        image_paths: list[str],
        response_schema: dict,
    ) -> dict:
        ...
```

Implement:

- `ScriptedAgentProvider`
- `OpenAICompatibleAgentProvider`
- `ReplayAgentProvider`

Do not hard-code the orchestration to one model vendor.

---

# 14. Agent output schema

```py
class AgentProposal(BaseModel):
    agent_id: str
    round_id: str
    summary: str
    observations: list[str]
    goals_addressed: list[str]
    actions: list[SceneAction]
    concerns: list[AgentConcern]
    request_another_view: list[CameraRequest]
    confidence: float
    should_pause_for_human: bool
```

Every action must be independently rejectable.

Agents may request a new camera view but may not directly control arbitrary camera coordinates. Allowed requests:

- overview
- north_elevation
- south_elevation
- east_elevation
- west_elevation
- top
- street_corner
- selected_component
- section_x
- section_z
- crane
- foundation

---

# 15. Agent system prompts

Store prompts as versioned files in `packages/agent-prompts`.

## 15.1 Shared system preamble

```text
You are an agent inside SkyFoundry, a conceptual 3D building-construction simulator.

You do not provide professional architecture, structural engineering, zoning, construction, safety, cost, or legal advice.

You cannot directly modify code or the Three.js scene. You may only propose schema-valid Building DSL actions.

Treat screenshots as incomplete visual evidence. Use the structured scene state as the source of truth for IDs, dimensions, levels, dependencies, and budgets.

Never invent an existing component ID. Never output executable code, URLs, shaders, filesystem paths, or prose outside the required JSON schema.

Prefer a small number of coherent actions. Reuse procedural generators. Use arrays for repeated components. Respect the lot, height, performance, and round budgets.

Every proposed action must include a concise rationale and identify the design goal it serves.

If the information is insufficient, request an allowed camera view or raise a concern instead of guessing.
```

## 15.2 Brief Interpreter

```text
Role: Brief Interpreter.

Convert the user's natural-language request into a conservative, explicit BuildingBrief.

Extract:
- location preset;
- tower use;
- approximate floors;
- podium floors;
- target height range;
- style;
- massing;
- façade preferences;
- public-realm requests;
- roof/crown requests;
- construction-animation interests;
- constraints;
- ambiguities.

Do not generate scene actions.
Do not infer professional zoning or code requirements.
When details are missing, choose editable concept defaults and label them assumptions.
```

## 15.3 Lead Architect

```text
Role: Lead Architect.

Own the overall concept and coordinate the specialist agents.

At the start, define:
- massing strategy;
- podium and tower relationship;
- floor and height strategy;
- core location;
- structural grid concept;
- façade rhythm;
- crown;
- public realm;
- visual priorities.

In later rounds:
- inspect screenshots and scene state;
- identify the single highest-value next design step;
- reconcile specialist proposals;
- avoid redesigning completed work without a clear reason;
- keep the tower coherent from street, skyline, and top views.

You may propose lot, level, grid, massing, public-realm, camera-cue, and high-level component actions.
You must not claim structural adequacy.
```

## 15.4 Structural Concept Agent

```text
Role: Structural Concept Agent.

Create a visually plausible conceptual load path using the provided grid and levels.

You may propose:
- core segments;
- columns;
- mega-columns;
- beams;
- transfer zones;
- braces;
- outriggers;
- slabs;
- foundation components.

Use simple regular systems.
Align vertical supports between levels unless a transfer element is explicitly introduced.
Do not calculate or claim real capacities, reinforcement, member sizing, wind response, seismic response, foundation performance, or safety.

Prioritize geometric consistency, support connectivity, constructability as a visual sequence, and low component complexity.
```

## 15.5 Façade Designer

```text
Role: Façade Designer.

Design the visible envelope as a repeatable parametric system.

You may propose:
- curtain-wall systems;
- panels;
- mullions;
- spandrels;
- punched-window walls;
- stone or brick bays;
- louvers;
- canopies;
- parapets;
- crown surfaces;
- night-lighting patterns.

Respect floor elevations and slab edges.
Use arrays and façade rules instead of individually authoring every panel.
Keep materials and panel sizes within browser budgets.
Use screenshot evidence to critique rhythm, proportion, corner treatment, podium transition, and crown termination.
```

## 15.6 Site Logistics Agent

```text
Role: Site Logistics Agent.

Make the construction site visually understandable.

You may propose:
- fence and gates;
- temporary office;
- crane location;
- hoists;
- vehicle routes;
- worker paths;
- material staging;
- scaffolding;
- safety rails;
- excavator and truck paths.

Keep equipment inside the site or defined access lane.
Avoid obvious collisions with the tower.
Do not claim a real logistics or safety plan.
Use a minimal number of equipment assets.
```

## 15.7 Construction Planner

```text
Role: Construction Planner.

Convert accepted building components into a visual construction-task DAG.

You may propose:
- task grouping;
- predecessors;
- phase;
- start tick;
- duration;
- equipment assignment;
- animation preset;
- camera cue.

Preserve valid dependencies:
site setup before excavation;
excavation before foundation;
foundation before supported structure;
lower floors before upper floors;
façade after a configurable structural lead;
public realm near completion.

The schedule is fictional and exists only to drive the animation.
```

## 15.8 Visual Critic

```text
Role: Visual Critic.

Inspect canonical screenshots and structured state.

Evaluate:
- silhouette;
- proportions;
- podium relationship;
- façade consistency;
- crown resolution;
- obvious floating or intersecting elements;
- visual repetition;
- street-level quality;
- construction readability;
- camera framing.

Return ranked concerns.
Propose at most five focused corrective actions.
Do not introduce a new design direction late in the run unless the current result clearly violates the user brief.
```

## 15.9 Build Controller

```text
Role: Build Controller.

You are the only agent node allowed to submit accepted actions for execution.

Review proposals against:
- schema;
- scope;
- dependencies;
- component budgets;
- phase;
- lot;
- support graph;
- collision reports;
- user brief.

Accept, reject, or request revision for each action.
Prefer partial acceptance over rejecting an entire useful proposal.
Provide concise reasons.
Do not alter an action silently.
```

---

# 16. Screenshot loop

## 16.1 Canonical cameras

Implement fixed camera rigs:

- skyline overview
- southwest street corner
- north elevation
- top view
- section X
- section Z
- crane view
- active-work close-up

## 16.2 Capture

The browser must expose a deterministic screenshot endpoint or command.

Options:

- Playwright visits a project route with camera query parameters;
- scene runtime captures canvas after assets settle;
- screenshots are written to an artifact directory;
- orchestrator receives local paths or uploaded image bytes.

Required naming:

```text
artifacts/{project_id}/round-{round}/overview.png
artifacts/{project_id}/round-{round}/street.png
artifacts/{project_id}/round-{round}/top.png
artifacts/{project_id}/round-{round}/work.png
```

## 16.3 Visual stability

Before capture:

- pause animation;
- wait for asset loading;
- set deterministic time of day;
- disable random traffic;
- set fixed device pixel ratio;
- wait two animation frames;
- render.

---

# 17. Scene context and Manhattan fixture

## 17.1 MVP fixture

Do not depend on a live map API.

Ship a local GeoJSON fixture containing:

- one Manhattan-like block;
- surrounding building footprints;
- approximate heights;
- streets;
- sidewalks;
- one empty lot.

The fixture may be based on permissibly licensed OpenStreetMap-derived data if attribution and source date are included, or it may be an original stylized fixture.

Display required attribution when using OSM-derived data.

## 17.2 Optional OSM importer

Implement a developer command that can transform a small GeoJSON/OSM extract into local scene coordinates.

Inputs:

- building footprints;
- `height`;
- `building:levels`;
- road polygons or centerlines;
- land-use polygons.

Fallback heights:

- explicit height;
- building levels × configured floor height;
- deterministic seeded category default.

Do not query public Overpass services repeatedly during normal browser use.

## 17.3 Surrounding buildings

Surrounding context should be:

- low-poly;
- extruded;
- muted;
- non-selectable by default;
- visually subordinate to the build site;
- batched for performance.

---

# 18. Physics

## 18.1 Required physics uses

Use Rapier for:

- ground collision;
- optional crane load swing;
- equipment collision bounds;
- sandbox drop mode;
- temporary falling-object demo;
- worker collision avoidance proxies.

## 18.2 Non-physics construction

Most assembly animation must remain deterministic and keyframed.

Do not make successful construction depend on unstable rigid-body placement.

## 18.3 Physics debug

Provide a developer toggle:

- colliders;
- rigid bodies;
- bounding boxes;
- support graph;
- contacts.

---

# 19. API

## 19.1 REST

```text
POST /api/projects
GET  /api/projects/:id
POST /api/projects/:id/brief
POST /api/projects/:id/run
POST /api/projects/:id/pause
POST /api/projects/:id/resume
POST /api/projects/:id/revise
GET  /api/projects/:id/actions
GET  /api/projects/:id/tasks
GET  /api/projects/:id/artifacts
POST /api/projects/:id/export
GET  /api/providers
```

## 19.2 Streaming events

Use WebSocket or SSE.

```ts
type ProjectEvent =
  | { type: "agent_started"; agentId: string; roundId: string }
  | { type: "agent_proposal"; proposal: AgentProposal }
  | { type: "validation_result"; result: ValidationResult }
  | { type: "actions_accepted"; actionIds: string[] }
  | { type: "scene_patch"; patch: ScenePatch }
  | { type: "task_started"; taskId: string }
  | { type: "task_progress"; taskId: string; progress: number }
  | { type: "task_completed"; taskId: string }
  | { type: "screenshot_ready"; screenshot: SceneScreenshot }
  | { type: "round_completed"; roundId: string }
  | { type: "run_completed"; projectId: string }
  | { type: "run_failed"; message: string };
```

## 19.3 Persistence

SQLite tables:

- projects
- briefs
- rounds
- agent_proposals
- actions
- validation_results
- components
- construction_tasks
- screenshots
- exports
- provider_calls

Store large scene snapshots as versioned JSON artifacts and keep references in SQLite.

---

# 20. Scene runtime

## 20.1 Component registry

The runtime must maintain:

```ts
type ComponentRecord = {
  id: string;
  type: ComponentType;
  objectRef?: THREE.Object3D;
  instanceRef?: {
    meshId: string;
    instanceIndex: number;
  };
  parentId?: string;
  levelId?: string;
  taskId?: string;
  state: "planned" | "staged" | "building" | "complete" | "removed";
  metadata: Record<string, unknown>;
};
```

## 20.2 Patch application

Scene mutations arrive as ordered patches.

Requirements:

- idempotent action IDs;
- action log;
- undo for non-destructive recent patches;
- deterministic replay from empty scene;
- patch validation before application;
- no React component remount for every instance.

## 20.3 Selection

Use raycasting and instance IDs.

On selection:

- highlight;
- show bounding box;
- focus camera;
- reveal component record;
- identify parent system;
- highlight dependencies optionally.

## 20.4 Section mode

Implement clipping planes for X and Z sections.

Section view should reveal:

- core;
- floors;
- columns;
- stairs;
- construction progression.

---

# 21. Building brief schema

```ts
type BuildingBrief = {
  projectName: string;
  locationPreset: "manhattan" | "generic" | "sandbox";
  buildingUse: Array<{
    use: "retail" | "office" | "residential" | "hotel" | "cultural" | "mixed";
    share: number;
  }>;
  targetFloors: {
    min: number;
    preferred: number;
    max: number;
  };
  targetHeightM?: {
    min: number;
    preferred: number;
    max: number;
  };
  podiumFloors: number;
  floorToFloorHeightM: number;
  styleKeywords: string[];
  massing: {
    type: "slab" | "point_tower" | "stepped" | "tapered" | "twisted_concept";
    setbacks: boolean;
  };
  structureConcept: {
    preferred: "core_and_frame" | "braced_frame" | "tube_concept";
  };
  facade: {
    primarySystem: "curtain_wall" | "punched_window" | "mixed";
    materials: string[];
    rhythm: "regular" | "expressive" | "vertical" | "horizontal";
  };
  crown: {
    type: "flat" | "tapered" | "lantern" | "mechanical_screen" | "garden";
  };
  publicRealm: string[];
  constructionFeatures: string[];
  assumptions: string[];
  unresolvedQuestions: string[];
};
```

---

# 22. Default tower recipe

When model access is absent, the scripted provider should build:

- 28 storeys;
- 3-storey stone podium;
- office tower;
- rectangular lot;
- central concrete core;
- regular column grid;
- tapered upper six floors;
- blue-gray curtain wall;
- vertical mullions;
- roof garden and mechanical crown;
- plaza with trees and benches;
- one tower crane;
- one external hoist;
- excavator, trucks, workers, and materials.

Construction should happen floor-by-floor with the façade trailing structure by four floors.

---

# 23. Performance targets

On a typical development laptop:

- load fixture scene in under 8 seconds after dev server is warm;
- maintain 45 FPS during normal orbit for default completed tower;
- remain above 30 FPS during typical construction animation;
- no more than 250 unique geometries;
- no more than 80 materials;
- no more than 150 active rigid bodies;
- no uncontrolled memory growth over a full replay;
- no browser console errors.

Use:

- instancing;
- merged static context geometry;
- texture atlases where useful;
- frustum culling;
- limited shadow casters;
- baked or simple lighting for context;
- configurable quality mode.

---

# 24. Visual style

Aim for:

- premium architectural visualization;
- clean clay-model readability;
- selective PBR materials;
- warm construction lighting;
- clear phase colors;
- cinematic camera easing;
- subtle atmospheric haze;
- restrained UI.

Modes:

- Realistic
- Clay
- Structure
- Construction
- Night
- X-ray

Structure mode colors systems by category, but color must not be the only identification method.

---

# 25. Accessibility

- keyboard-accessible non-canvas UI;
- visible focus;
- labeled controls;
- pause animation;
- reduced-motion mode;
- high-contrast UI;
- text alternative summarizing the current construction state;
- no flashing;
- timeline usable without drag only;
- canvas selection mirrored in a component tree.

---

# 26. Security

## 26.1 Model outputs

- validate all model output;
- reject extra fields;
- cap string length;
- cap arrays;
- no `eval`;
- no generated JSX;
- no generated shader code;
- no arbitrary HTML;
- escape user text;
- record provider output.

## 26.2 CAD

- sandbox;
- no network;
- no secrets;
- no arbitrary host paths;
- timeout;
- resource limits;
- allowlist;
- output scan.

## 26.3 External assets

- allowlist file types;
- check size;
- validate GLB;
- run mesh simplification;
- reject external scripts;
- preserve licenses and source metadata.

---

# 27. Observability

Record:

- project run ID;
- round ID;
- agent;
- provider;
- prompt version;
- model;
- latency;
- input screenshot hashes;
- output schema result;
- accepted action count;
- rejected action count;
- component delta;
- validation warnings;
- browser FPS sample;
- screenshot paths;
- errors.

Provide a developer diagnostics drawer.

---

# 28. Tests

## 28.1 Unit tests

- BuildingBrief validation
- DSL validation
- ID generation
- grid placement
- level generation
- component arrays
- support graph
- collision classification
- lot bounds
- task DAG
- animation timing
- budget limits
- patch idempotency
- deterministic replay

## 28.2 Contract tests

- scripted agent provider
- multimodal provider adapter
- CAD worker
- asset provider
- screenshot service
- persistence
- streaming events

## 28.3 Integration tests

- brief to accepted concept actions;
- actions to component registry;
- components to construction tasks;
- task playback to completion;
- screenshot to next agent round;
- revision to scoped scene patch;
- export and re-import;
- no-key deterministic mode.

## 28.4 End-to-end tests

Playwright:

1. Open landing page.
2. Select Manhattan preset.
3. Use the default tower prompt.
4. Start session.
5. Observe agent round.
6. Wait for first accepted scene patch.
7. Verify site setup appears.
8. Advance to structure.
9. Select a column.
10. Open component inspector.
11. Switch to section view.
12. Pause.
13. Scrub backward.
14. Resume.
15. Request “make the crown more tapered.”
16. Review preview.
17. Approve.
18. Verify crown changes.
19. Replay.
20. Export project JSON.

Run in Chromium.

## 28.5 Visual regression

Capture:

- empty Manhattan lot;
- site setup;
- foundation;
- ten floors;
- complete structure;
- partial façade;
- completed daylight;
- completed night;
- section;
- mobile viewer;
- reduced motion.

---

# 29. Evaluation

## 29.1 Action validity

Target:

- scripted provider: 100% schema-valid;
- live model: greater than 90% schema-valid after one repair;
- zero direct scene mutations outside DSL.

## 29.2 Visual plausibility

Automated checks:

- no unsupported columns;
- no duplicate component IDs;
- no beams with missing endpoints;
- no façade panel beyond lot-derived envelope;
- no crane through tower;
- no task cycles;
- no component created before predecessor task.

## 29.3 Agent usefulness

For each round:

- at least one accepted action or an explicit reason no action is needed;
- no repeated identical rejected action;
- no late global redesign after the review threshold;
- max action budget respected.

## 29.4 Determinism

Given the same fixture and seed:

- identical brief;
- identical action IDs;
- identical component count;
- identical task DAG;
- screenshots within visual tolerance.

---

# 30. Milestones

## Milestone 0 — Repository and verification harness

Deliver:

- monorepo;
- commands;
- AGENTS.md;
- PROGRESS.md;
- schemas;
- fixture artifacts;
- CI-ready checks;
- basic landing page.

Verify:

```bash
pnpm install
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Milestone 1 — Three.js city sandbox

Deliver:

- Manhattan fixture;
- lot;
- surrounding buildings;
- roads and sidewalks;
- camera controls;
- lighting;
- scene modes;
- selection skeleton.

Verify manually and with Playwright screenshot.

## Milestone 2 — Building DSL and procedural factory

Deliver:

- schemas;
- component registry;
- patch application;
- generators;
- materials;
- instancing;
- grid and level definitions.

Create a static 12-storey tower entirely from JSON.

## Milestone 3 — Construction timeline

Deliver:

- task DAG;
- phases;
- timeline;
- animation presets;
- pause/resume/scrub;
- crane;
- workers;
- vehicles;
- deterministic replay.

## Milestone 4 — Scripted agent studio

Deliver:

- FastAPI orchestrator;
- LangGraph graph;
- scripted agent provider;
- streaming;
- agent panel;
- validation;
- six-round default build.

At this milestone the full product loop must already work without an API key.

## Milestone 5 — Screenshot feedback loop

Deliver:

- canonical cameras;
- capture service;
- artifact storage;
- visual critic round;
- screenshot viewer;
- deterministic capture.

## Milestone 6 — Live multimodal provider

Deliver:

- generic provider interface;
- one OpenAI-compatible implementation;
- structured outputs;
- screenshot attachments;
- retry and repair;
- timeout and budget;
- replay provider.

Do not block completion if credentials are unavailable.

## Milestone 7 — Revisions

Deliver:

- revision parser;
- affected-component resolver;
- preview;
- approval;
- demolition/replacement animation;
- undo.

## Milestone 8 — CAD adapter

Deliver:

- constrained CAD recipe;
- trusted templates;
- sandboxed CadQuery worker;
- one custom bracket or planter demo;
- GLB import.

Skip raw generated Python in normal mode.

## Milestone 9 — Optional generative asset adapter

Deliver interface, mock provider, documentation, and asset-ingestion pipeline.

Do not download or install TRELLIS automatically.

## Milestone 10 — Polish and QA

Deliver:

- final visual design;
- reduced motion;
- accessibility pass;
- diagnostics;
- exports;
- README;
- screenshots;
- no console errors;
- all tests passing.

---

# 31. Overnight execution priorities

Codex must follow this order:

1. Get the deterministic scene and scripted construction loop working.
2. Make it visually impressive.
3. Make the DSL and validation reliable.
4. Add the agent studio using scripted agents.
5. Add the screenshot loop.
6. Add live multimodal provider only after the fixture passes.
7. Add CAD only after the core product works.
8. Treat TRELLIS as an optional documented integration.

Do not spend the night trying to install GPU tooling, query live OSM, or perfect CAD export while the core browser experience is incomplete.

---

# 32. AGENTS.md requirements

Create `AGENTS.md` with these rules:

- Read `PLAN.md` and `PROGRESS.md` before work.
- Update `PROGRESS.md` after each milestone.
- The deterministic no-key demo is the highest priority.
- Do not let models write arbitrary runtime code.
- All scene mutations use the Building DSL.
- All external/model output is schema validated.
- Never claim engineering validity.
- Do not install TRELLIS in the default environment.
- Do not execute unrestricted CadQuery.
- Run focused tests after each change.
- Run full checks before claiming completion.
- Use Playwright to inspect the actual rendered app.
- Capture screenshots after major visual milestones.
- Fix console errors.
- Preserve stable component IDs.
- Prefer simple, robust visual systems over speculative complexity.
- Record architectural decisions in `docs/decisions/`.
- Document any unimplemented optional capability explicitly.

---

# 33. Optional Codex subagents

Configure project-scoped subagents if supported:

## Architecture reviewer

Read-only. Checks boundaries, dependency direction, DSL purity, and state ownership.

## Three.js performance reviewer

Read-only. Checks instancing, draw calls, disposal, texture sizes, shadows, and render-loop issues.

## Browser QA agent

Runs the app, exercises the demo, captures screenshots and console logs, and reports defects.

## Agent-safety reviewer

Checks schema validation, prompt injection boundaries, tool permissions, and CAD sandboxing.

## Test reviewer

Checks deterministic coverage, false-positive mocks, flaky tests, and missing E2E assertions.

The primary Codex agent remains responsible for edits and final integration.

---

# 34. Environment variables

```bash
# Core
DATABASE_URL=sqlite:///./data/skyfoundry.db
ARTIFACT_DIR=./artifacts
AGENT_PROVIDER=scripted
AGENT_SEED=42

# Web/orchestrator
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000
ORCHESTRATOR_PORT=8000

# Optional multimodal API
MULTIMODAL_API_KEY=
MULTIMODAL_BASE_URL=
MULTIMODAL_MODEL=
ENABLE_LIVE_AGENTS=false

# Optional CAD
ENABLE_CAD_WORKER=false
CAD_WORKER_URL=http://localhost:8010
CAD_JOB_TIMEOUT_SECONDS=20

# Optional TRELLIS-compatible service
ENABLE_TRELLIS=false
TRELLIS_ENDPOINT=
TRELLIS_API_KEY=

# Optional map import
ENABLE_OSM_IMPORT=false
```

The project must boot without optional variables.

---

# 35. Definition of done

The goal is complete only when:

- `pnpm install` succeeds;
- `pnpm build` succeeds;
- lint and type checking pass;
- unit and integration tests pass;
- Playwright E2E passes;
- the deterministic Manhattan demo runs without external keys;
- the user can submit the default prompt;
- agents visibly collaborate;
- only typed actions mutate the scene;
- actions are validated;
- the tower is animated through all construction phases;
- the scene is pannable, orbitable, and zoomable;
- the timeline can pause, scrub, resume, and replay;
- columns, beams, slabs, core, façade panels, crane, workers, and site equipment are visible;
- a component can be selected and traced to its agent/action/task;
- a crown revision can be previewed and applied;
- project JSON export works;
- at least one screenshot export works;
- no browser console errors appear in the demo;
- reduced-motion mode works;
- performance remains usable;
- documentation distinguishes implemented, optional, and conceptual functionality;
- the professional-use disclaimer is visible;
- optional GPU/CAD providers cannot break the base app;
- `PROGRESS.md` accurately records results and remaining limitations.

---

# 36. Completion report

At the end, Codex must write `FINAL_REPORT.md` containing:

- what was implemented;
- how to run it;
- tests and exact results;
- screenshots and paths;
- architecture summary;
- model-provider status;
- CAD-provider status;
- TRELLIS-provider status;
- performance measurements;
- known limitations;
- next five highest-value improvements;
- any blocked items with evidence.

Do not claim success without launching the app and completing the default E2E flow in a browser.