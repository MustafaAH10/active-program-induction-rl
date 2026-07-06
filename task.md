# Active Program Induction — Benchmark Design & Build Document (v2, amended)

**Project one-liner.** Train a small model (Qwen3-8B class) with RL to *actively probe a hidden program, infer its behavior, and submit an equivalent implementation*, and show that the learned **"design informative experiments"** skill is real and transfers. The differentiator vs. Absolute Zero Reasoner (AZR) and DeepCoder-style induction is that examples are **not handed to the solver**; the solver **chooses its own probes**, multi-turn.

> **What changed in v2.** This version folds in review feedback. Three things are corrected outright (DSL equivalence, the "optimal-probe" overclaim, and the contamination wording). The project is restructured as **one phased program with a de-risk gate**, not a smaller project — full scope stays on paper, but every phase starts from a validated base. The **headline claim is narrowed on purpose**: the load-bearing result is *learned active experimentation* (Active > Passive); coding-benchmark improvement is framed as **upside**, not the thing the project depends on. Training-data scale is fixed (online generation for training, a frozen suite for eval), and a new **RL feasibility + cold-start calibration** section is added.

---

## 0. Project framing: one project, three phases, one de-risk gate

The full system is ambitious; the *first validated result* should be small and safe. These are not in tension — they're a build order. Read the whole taxonomy below as the project; read Phase 1 as what runs in week two.

- **Phase 1 — Proof of life (low risk).** Families A (automata) + C (Boolean junta/tree). `base vs Passive-trained vs Active-trained` on held-out tasks, reporting correctness, query counts, and the Active–Passive gap. This alone validates the benchmark idea and the training loop. **← de-risk gate: nothing downstream is built until this shows a gap.**
- **Phase 2 — Synthesis framing (medium risk).** Add Family B (bounded DSL) with the equivalence fix in §4. Turns "toy formal languages" into "program synthesis."
- **Phase 3 — Realism + transfer (upside).** Transfer evals (§7) and optionally Family D (terminal binary). This is where employability lives, and its risk is near-zero *conditional on* Phase 1 working.

**The claim to protect.** The first result is about **learned active experimentation**, not broad coding improvement. If coding benchmarks improve later, that is upside, not the load-bearing claim. This framing is insurance: our own §8 analysis says the *likely* outcome is "code-reasoning up, raw synthesis flat" — under an experimentation-first headline that outcome is a clean success; under a coding-first headline the same numbers read as failure. Same experiments, more robust framing.

---

## 1. The core task

Every task is a black box (the *oracle*) implementing a hidden function `f`. The agent runs an episode:

```
obs = env.reset(task_id)          # task spec: type signature, format, budget
while not done:
    action = policy(obs)
    obs, reward, done, info = env.step(action)

# action ∈ {
#   {"tool": "query_oracle",   "input": <x>}        # observe f(x)
#   {"tool": "run_solution",   "input": <x>}        # test own candidate on x
#   {"tool": "write_solution", "code": "<src>"}     # (re)write candidate
#   {"tool": "submit"}                              # end episode, trigger grading
# }
```

Reward is **mostly terminal**:

```
final_reward = equivalence(submitted, hidden)  -  ε * num_queries  -  penalties
```

with a small per-probe cost `ε` (e.g. 0.002) plus tiny penalties for invalid actions / timeouts. **No dense hand-crafted "information gain" reward.** The per-query cost alone forces efficient, discriminating probing: the only way to score well is to identify `f` in few queries, which requires probing where competing hypotheses disagree.

### Why this is not AZR

AZR's induction mode gives the solver a *fixed* example set as part of the task. Here the solver **selects examples adaptively based on what it has already observed**. That splits the skill into (1) synthesis (same as everyone) and (2) *experiment design* (new, and the whole point). We isolate (2) with a **Passive vs Active** ablation at matched compute — the gap between them is our headline number.

---

## 2. Task taxonomy — the "program and terminal tasks" we generate

We span *formally clean* (decidable equivalence, exact difficulty metrics) to *agentic/terminal* (realistic, fuzz-graded). Building several families lets us claim cross-family transfer and reuse one equivalence-checked grader per family.

| Family | Oracle | Equivalence check | Difficulty knob | Phase / role |
|---|---|---|---|---|
| **A. Automata** | DFA (accept/reject) or Mealy (string→string) | **Exact & cheap** — product automaton + BFS for shortest distinguishing string | # states, alphabet | **Phase 1.** Cleanest theory; exact difficulty + query-efficiency metric |
| **C. Boolean junta / tree** | `f:{0,1}^n→{0,1}` depending on only k of n bits | **Exact** — enumerate relevant subspace / SMT | n, k, depth | **Phase 1.** Makes the *value of active probing* starkest (random probing is exponential; adaptive is fast) |
| **B. Bounded DSL** | Composition of list/string primitives | **Decidable *only if bounded*** — see §4 fix | # composed ops | **Phase 2.** "Program synthesis" framing |
| **D. Terminal mystery-binary** | Executable in a shell sandbox; probe via stdin/args | **Fuzz-equivalence (probabilistic)** — weaker rigor, hack risk | I/O complexity, statefulness | **Phase 3, optional.** Realism/résumé extension, **not** part of the core claim |
| **E. SQL/view induction** *(optional)* | Hidden query; agent supplies small DB states | Decidable for bounded schemas | # joins, aggregation | Optional, later. |

**Recommended order:** A + C together (Phase 1) → B (Phase 2) → D/E (Phase 3, optional). C is a cheap high-value add because its Passive-vs-Active gap is dramatic.

**Shared property of A/B/C/E:** *decidable equivalence*, which buys a reward memorization can't hack, an exact per-task difficulty measure, and (for A) a query-efficiency metric. Family D trades that rigor for realism, so keep it a minority and out of the core claim.

---

## 3. Two generation sources (and the "no distillation" claim)

- **Procedural generators (pure Python).** Reliable, controllable, zero distillation concern. Backbone for A and C (random *minimal* DFAs, random k-juntas) and the DSL skeleton in B. **This is also how we generate training data at scale — see §5.**
- **Frozen-model generator (the initial Qwen checkpoint).** Proposes tasks where *semantic diversity* matters (DSL surface language in B, terminal tasks in D, natural-language descriptions). Supports the "self-generated, no *frontier* teacher" narrative.

The distillation objection ("you just distilled a frontier model") is answered because the only model in the loop is a frozen copy of the model we train; procedural generation is even more obviously not-distillation. **§6 exists to test whether Qwen is good enough to serve as the frozen generator for B/D.** If it isn't, we fall back to procedural generation and the project is still fully valid, just with a weaker self-generation story.

---

## 4. Non-gameability: held-out grading + the generator filter + the DSL fix

Two rules make A/C/(bounded-)B/E non-gameable and defang the "lookup-table / trivial if-else" hack:

1. **Grade on equivalence over the whole space, never on probed points.** A memorizing solver that submits `if x in observed: return observed[x] else <junk>` fails equivalence instantly — the equivalence oracle finds a short *unprobed* input where lookup ≠ truth — so `correct = 0` and, having paid for its probes, its reward goes **negative**. Ordering falls out: correct-and-lean > correct-but-wasteful > any memorizer.
2. **Keep |input space| ≫ probe budget, and reject non-dense tasks at generation.** "Needle" functions (behavior on a measure-zero input set) are un-probeable, un-fuzzable, and the only place lookups could win. Reject them.

It is **fine for the true hidden program to be an if-else / decision tree.** We forbid the *solver memorizing observed leaves*, not branchy solutions. Held-out equivalence grading distinguishes "learned the structure" from "memorized the points I saw."

### ⚠️ DSL equivalence fix (Family B) — corrected from v1

**The hole:** if the hidden task is a DSL program but the model may submit *arbitrary Python*, "decidable equivalence" is false in general — you cannot decide equivalence of two arbitrary Python functions. v1 glossed this. **Fix, in two tiers:**

- **Phase-2 early: require submissions in the same DSL / as an AST.** Then equivalence is decidable within the DSL (bounded enumeration or SMT over the DSL's semantics). This is the rigorous default.
- **Phase-2 later (optional): allow free-form Python, but only with a *bounded* input domain small enough to enumerate exhaustively.** Equivalence then means "agrees on every input in the (finite) domain." State the bound explicitly; outside it you have no guarantee.

Never claim exact equivalence for unbounded-domain free-form Python submissions. If you want free-form Python on an unbounded domain, you are in *fuzz-equivalence* territory (Family D's regime) and must label it as probabilistic.

### The generator filter (execution-only; no teacher model)

```python
def acceptable(M, L=8):
    labels = [run(M, w) for w in sample_inputs(space, L)]   # cheap execution
    p = positive_rate(labels)
    if p < 0.05 or p > 0.95:      # 1. near-constant → trivial & lookup-friendly
        return False
    if not is_canonical(M):       # 2. minimal DFA / canonical form → no fake difficulty
        return False
    if trivial_complexity(M):     # 3. solvable in <2 probes → active skill not exercised
        return False
    if flip_rate(labels) < 0.15:  # 4. behavior must be dense so held-out grading is meaningful
        return False
    # 5. band difficulty: base-model active pass@1 in a learnable window (see §6, §8b)
    return True
```

Rule 5 (measured with the base model as solver) keeps tasks "hard but not impossible" so RL gets gradient — and matches TMax's free-filtering insight: during RL, any task where all rollouts get identical reward contributes no gradient and is effectively discarded, so the filter only needs to be approximately right.

### Reward, with an anneal for cold-start sparsity

```python
def final_reward(submitted, hidden, num_queries, EPS=0.002, mode="exact"):
    if mode == "graded":   # early training: dense signal
        correct = fraction_agreeing_up_to_length(submitted, hidden, L=10)  # continuous [0,1]
    else:                  # later: exact
        correct = 1.0 if equivalent(submitted, hidden) else 0.0
    return correct - EPS * num_queries
```

Start `graded`, anneal to `exact`. The graded mode is not a nicety — it is the primary defense against cold-start reward sparsity (see §8b).

### Metric wording fix — corrected from v1

Product-automaton BFS gives the **shortest distinguishing string between two given machines**. It does **not** by itself give an **optimal active-probing policy over the whole hypothesis class** — that is a harder active-learning problem. So:

- **Report:** shortest-counterexample length, queries-to-solve, and query efficiency (queries used vs. a reasonable reference such as an L\*-style learner *if you actually implement one*).
- **Do not call** the BFS distinguishing string an "optimal-probe reference." Only use "optimal" if you implement a genuine optimal policy over a finite candidate set (feasible for small automata; state it as such).

---

## 5. Composition axes, training data, and the fixed eval suite

Following TMax, sample each task by drawing one value per axis so the set is combinatorially diverse and balance falls out of structure.

**Axes:** `family` · `difficulty_tier` ∈ {easy, medium, hard} · `oracle_complexity` · `input_domain` · `probe_budget` ∈ {8, 16, 32} · `description_style` ∈ {terse, natural, adversarial} · `distractor_density`.

### Training vs. evaluation — corrected from v1

- **Training: online procedural generation (unbounded).** Generate fresh tasks on the fly during RL, gated through `acceptable()`. This gives effectively infinite non-repeating training data and removes overfitting-to-a-fixed-set as a concern. The 2,700-task figure is *not* the training set.
- **Evaluation: a frozen suite of ~2,700 tasks**, sampled once and held fixed, with per-(family × tier) balance. Hold out ~15% of each cell as an in-distribution test split, and keep **one entire `input_domain` per family unseen** (e.g. train Family B on integer/list transforms, evaluate on string transforms) as the **near-transfer ring** (§7).

### Contamination wording fix — corrected from v1

Contamination is **structurally impossible for our internally generated tasks** (every task freshly sampled, graded on held-out inputs). This is **not** true of public benchmarks (HumanEval, MBPP, CRUXEval, ARC), which may appear in pretraining corpora. Treat public-eval numbers as *suggestive of transfer*, controlled by the `base vs Passive vs Active` comparison (all three share the same contamination, so *differences* between them remain meaningful even if absolute numbers are inflated).

---

## 6. Testing whether Qwen can generate (and solve) this

Before committing, run these against **Qwen3-8B** (and Qwen3.5-9B if available). Three separate capabilities: **(6.1)** can it *solve* at all (sets your RL starting point + difficulty calibration — this is also the go/no-go gate of §8b), **(6.2)** can it *generate* valid non-trivial tasks (viability of the frozen generator for B/D), **(6.3)** does it generate *diverse* tasks or collapse. §6.4 gives go/no-go thresholds.

> Setup: temperature 0.7, n=8 samples, score with your `acceptable()` filter and equivalence checker (not the model's self-reports). All prompts request strict JSON.

### 6.1 Solver-calibration prompts

**6.1.a — Passive baseline (fixed examples).**
```
SYSTEM:
You are given input→output examples produced by a single hidden Python
function f. Infer f and return ONLY its source as JSON:
{"code": "def f(x): ..."}. No prose, no markdown fences.

USER:
f([1,2,3,4]) = [4,8]
f([0,-1,-2,5]) = [0,-4]
f([2,2,3,3,4]) = [4,4,8]
Return the function.
```

**6.1.b — Active induction (the real task; run as a real multi-turn loop).**
```
SYSTEM:
There is a hidden function f: list[int] -> list[int]. Investigate it by
issuing probes, then submit an implementation. On each turn output EXACTLY
ONE JSON action:
  {"tool":"query","input":[...]}            # observe f(input)
  {"tool":"submit","code":"def f(x): ..."}  # end and be graded
Budget: 16 probes; fewer is better. Probe inputs where plausible hypotheses
would DISAGREE. Output only the JSON.

USER:
Begin. Signature is f: list[int] -> list[int]. Make your first action.
```
*(Each turn: parse the action; if `query`, reply `{"result": f(input)}`; if `submit`, score. Log #probes and whether probes hit disagreement points.)*

**6.1.c — Automata solver probe (Family A, exact-gradeable).**
```
SYSTEM:
A hidden DFA over alphabet {a,b} labels strings accept/reject. Investigate
by querying strings, then submit the DFA as JSON:
{"states":[...],"start":...,"accept":[...],"delta":{"q0,a":...,...}}.
Each turn output ONE JSON action:
  {"tool":"query","input":"aba"}
  {"tool":"submit","dfa":{...}}
Budget: 20 queries. Query strings on which competing rules disagree.

USER:
Begin. Alphabet {a,b}, empty string allowed. Make your first action.
```

### 6.2 Generator prompts (frozen-generator viability)

**6.2.a — DSL task generator (Family B).**
```
SYSTEM:
You generate program-induction tasks. Produce ONE hidden Python function
over lists of integers, built by composing simple primitives (map, filter,
running-sum, reverse, dedup, take/drop, zip-with-neighbor, elementwise
arithmetic). Requirements:
- deterministic, total (never raises) on any list of ints length 0..20
- NOT constant, NOT identity, NOT dependent on a single magic input
- behavior visibly changes as inputs vary
Return ONLY JSON:
{"code":"def f(x): ...",
 "one_line_spec":"english description",
 "difficulty_self_estimate":"easy|medium|hard",
 "three_disambiguating_probes":[[...],[...],[...]]}
No markdown fences.

USER:
Generate one medium-difficulty task with a non-obvious near-miss.
```

**6.2.b — DFA task generator (Family A).**
```
SYSTEM:
Generate a hidden DFA over alphabet {a,b}. Return ONLY JSON:
{"dfa":{"states":["q0",...],"start":"q0","accept":[...],
        "delta":{"q0,a":"q1","q0,b":"q0",...}},
 "regex_or_english":"language description","num_states":N}
Constraints: 3–6 states, minimal (no two equivalent states), non-trivial
language (not 'everything'/'nothing'/'single fixed string'); acceptance
must require tracking state across the string. No markdown.

USER:
Generate one DFA whose language is easy to state but easy to confuse with a
near-miss (e.g. "contains aa" vs "ends with aa"). Medium.
```

**6.2.c — Terminal mystery-binary generator (Family D).**
```
SYSTEM:
Generate a self-contained Python script acting as a hidden "mystery binary".
It reads one line of stdin (a JSON value) and prints one line of stdout (a
JSON value), implementing a deterministic transformation. It must never
crash on any JSON list/string/int input, be total and deterministic (no
randomness/time/network/files), and be non-trivial but inferable in ~15
probes. Return ONLY JSON:
{"script":"<full python source>","english_spec":"...",
 "sample_probe":<json>,"expected_on_sample":<json>,
 "difficulty":"easy|medium|hard"}
No markdown fences.

USER:
Generate one medium task whose behavior is stateful across list elements
(so single-element probes underdetermine it).
```

**6.2.d — Natural-language wrapper generator (tests the "read the spec" skill).**
```
SYSTEM:
Rewrite the following formal function spec as a natural-language task
description, burying at least one condition in a subordinate clause and
phrasing one condition in the negative. Do not change behavior.
Return ONLY JSON: {"natural_language_spec":"..."}

USER:
Formal spec: "Return the running maximum of the list, but reset the running
maximum to 0 whenever a negative number is encountered."
```

### 6.3 Diversity audit prompt
```
SYSTEM:
Audit a batch of generated induction tasks for DIVERSITY. Given one-line
specs, cluster by underlying operation type and report distinct cluster
count, the 3 most over-represented patterns with counts, and near-duplicate
groups. Return JSON:
{"n_clusters":K,"over_represented":[{"pattern":"...","count":N}...],
 "near_duplicate_groups":[[i,j,...],...]}

USER:
Specs:
1. <spec>
...
200. <spec>
```

### 6.4 Go / no-go for using Qwen as generator
Run 6.2 at n≥200/family; score with *your* filter and checker:
- **Validity** (passes `acceptable()`) ≥ **40%** (fall back to procedural below ~20%).
- **Non-triviality**: base-model active pass@1 in **[0.15, 0.75]** for the bulk.
- **Diversity** ≥ **15** distinct clusters / 200; if top-3 patterns > 50%, add axis-conditioning or fall back to procedural.
- **Determinism/totality** ≥ **95%** after filtering (hard correctness gate).

If B/D miss thresholds, generate A/B/C procedurally and keep the frozen generator only for NL wrappers (6.2.d) — the easiest job, most likely to pass.

---

## 7. Transfer evaluation

External benchmarks are the **falsification test**: if the model only got good at its own distribution, external scores stay flat. Three rings.

**Ring 1 — held-out task families (you build; tests the actual claim).** Train on some input domains, evaluate zero-shot on disjoint ones (integer→list trained → string/dict/matrix; DFA → Mealy). Measures whether the *probing strategy* generalizes. **Headline number**, reported with the **Passive-vs-Active gap at matched compute**.

**Ring 2 — public code-reasoning (credibility; solving half).**
- **CRUXEval** — CRUXEval-I (input prediction ≈ abduction), CRUXEval-O (output prediction ≈ deduction); adjacent skills, hard, not predicted by HumanEval.
- **ARC-AGI** — canonical few-shot induction, *off* code (tests modality transfer).
- **MBPP+ / HumanEval+** — straight synthesis; confirm no regression.
- **LiveCodeBench** — contamination-resistant coding.

**Ring 3 — far transfer (skeptical).** GSM8K/MATH, BBH. Flat is fine and publishable; positive is bonus.

**Contamination caveat (see §5):** public-eval *absolute* numbers may be inflated by pretraining exposure, but the **base vs Passive vs Active differences** remain meaningful because all three share the same exposure. Lead with the differences, not the absolutes.

**The rigor control:** `base vs Passive-trained vs Active-trained` at matched compute across all rings. If only Active improves on experimentation-flavored evals while Passive matches it on static synthesis, the contribution is isolated from "any code RL helps."

---

## 8a. Will coding performance improve? — honest read

**Short answer: plausibly yes for code *reasoning/execution*, weakly-to-moderately for code *generation*, and it's an empirical question Ring 2 is built to answer — but per §0 it is upside, not the load-bearing claim.**

**Why it should help.** The task trains (1) mentally executing a program to predict behavior on chosen inputs (= CRUXEval-O), (2) reasoning backward from behavior to structure (= CRUXEval-I / abduction), (3) synthesizing a consistent program. Precedent: AZR, training on self-generated code induction/deduction/abduction with an execution-checked reward, reported SOTA coding+math with zero external data and strong cross-domain transfer (its coder variant improved math ~10.9 pts vs ~0.65 for standard RLVR).

**Why it might underdeliver, and how you'll know.** Our task is narrower than general coding. Honest risks: (a) probing skill transfers to interactive/agentic evals but gives only modest lift on *static* synthesis (which was never the bottleneck we trained); (b) narrow task distribution → narrow transfer. Evals disambiguate: CRUXEval + ARC up with HumanEval+ flat means "improved code *reasoning*, not code *writing*" — a strong, correctly-scoped claim. Passive-vs-Active tells you whether any lift is the experimentation skill or just more code exposure.

**Success ladder (strongest first):** (1) Active > Passive on Ring-1 + an interactive eval; (2) clear CRUXEval-I/O lift over base; (3) non-regression on MBPP+/HumanEval+; (4) ARC lift. Hitting (1)+(2)+(3) is a strong portfolio result; (4) and Ring 3 are upside.

---

## 8b. Is RL training feasible? — feasibility read + the cold-start gate

**Infrastructure: high feasibility (~95%).** GRPO on Qwen3-8B (or 4B) with LoRA on a single H100/A100-80GB, ~100–150 steps, is a few days and ~$100–300. Multi-turn tool-use GRPO on a single node is well-trodden (`verifiers`, TRL GRPO, SkyRL/veRL). The reward is a pure Python float (the easy case — no reward model, no human labels), and online procedural generation removes data scarcity.

**The real risk is cold-start reward sparsity, not compute.** GRPO learns from *variance within a rollout group*. If the base model almost never solves a task, every rollout scores ≈0, advantages vanish, and training flatlines. Defenses (treat as load-bearing, not optional):
- **Graded reward** (fraction-agreed, annealing to exact) so early attempts get partial signal.
- **Difficulty banding** to tasks with base active pass@1 in ~[0.15, 0.75].
- **Curriculum**: start on 2–3 state DFAs / small juntas, grow.

**Secondary risks:** multi-turn stability on long episodes (mitigate: cap probe budget at 8–16 early, tiny strictly-parsed action space, hard turn caps, 100–150 steps — you likely won't need TMax's DPPO/FP32-head/async machinery at this scale); and harness/eval cost (multi-turn plumbing — state, JSON parsing, timeouts, sandboxed `run_solution` — is where the bugs and the time go; budget more for the harness than the training).

### ★ The cold-start calibration gate (do this before building the training loop)
Run base Qwen3-8B through the active Family-A loop, n=8 rollouts/task, ~200 easy-tier tasks, and inspect the **reward distribution**:
- **Spread of rewards (some solves, some fails, some partials)** → GRPO has gradient to climb → **green light** to build training.
- **All-zeros even on the easiest tier** → difficulty/observation-format is wrong → fix *before* spending on GPUs.

This single measurement moves the probability of a successful Active-over-Passive result from ~40% (train blind) to ~70% (train after the gate clears). It is the highest-leverage step in the plan and costs ~$0 in GPU time.

**Bottom line.** The *core* result — a measurable Active > Passive gap on Family A/C held-out tasks — depends only on the two high-feasibility families and a reward you fully control, and is a fairly safe yes *conditional on the cold-start gate*. Everything downstream (DSL, transfer, coding) is upside on a base that's very likely to hold.

---

## 9. Build order (phased, with the de-risk gate)

**Phase 1 — Proof of life (Families A + C).**
1. Procedural minimal-DFA generator → canonical minimization → `acceptable()` filter.
2. Four-action env (`query` / `run` / `write` / `submit`); graded→exact reward via product-automaton BFS.
3. Add Family C (k-junta) — cheap, and where active probing shines.
4. **Cold-start calibration gate (§8b):** base Qwen active-vs-passive on easy tier. *Green light required to proceed.*
5. Passive baseline (fixed examples from the same oracles).
6. Train Active vs Passive with GRPO at matched compute (online generation; graded→exact anneal; short episodes).
7. **De-risk gate / first milestone:** `base vs Passive-trained vs Active-trained` on held-out A+C, with correctness, query counts, and the Active–Passive gap.

**Phase 2 — Synthesis framing (Family B).** Add bounded DSL with the §4 equivalence fix (DSL/AST submissions first; bounded-domain Python later). Re-run the three-way comparison.

**Phase 3 — Realism + transfer (upside).** Transfer evals (§7, all three rings, differences-not-absolutes). Optionally add Family D (terminal binary) as a labeled fuzz-graded realism extension, kept out of the core claim.

**First publishable milestone:** end of Phase 1 — learned active experimentation demonstrated on decidable families. Everything after is strictly additive on a validated base.

The generator, the filter, and the equivalence-checked reward are where your time goes. The RL run — as in TMax — is almost the easy part, *once the cold-start gate is green.*

---

## 10. Full worked examples

These are concrete examples of what a generated task, an active episode, and a submitted solution look like. The hidden oracle is shown here for documentation only; the agent receives only the public observation and oracle responses.

### Example A1: Family A, DFA induction

**Hidden oracle (not shown to agent).** DFA over alphabet `{a,b}` accepting strings that end with `"ab"`.

```json
{
  "family": "automata",
  "task_id": "dfa_ends_with_ab_easy_0001",
  "alphabet": ["a", "b"],
  "hidden_dfa": {
    "states": ["q0", "q1", "q2"],
    "start": "q0",
    "accept": ["q2"],
    "delta": {
      "q0,a": "q1",
      "q0,b": "q0",
      "q1,a": "q1",
      "q1,b": "q2",
      "q2,a": "q1",
      "q2,b": "q0"
    }
  }
}
```

**Initial observation shown to agent.**

```json
{
  "family": "automata",
  "signature": "f: string over {a,b} -> bool",
  "alphabet": ["a", "b"],
  "empty_string_allowed": true,
  "probe_budget": 8,
  "actions": ["query", "submit"],
  "submission_format": {
    "states": "list[str]",
    "start": "str",
    "accept": "list[str]",
    "delta": "map['state,symbol' -> 'state']"
  }
}
```

**One active transcript.**

```json
[
  {"agent": {"tool": "query", "input": ""}, "env": {"result": false}},
  {"agent": {"tool": "query", "input": "ab"}, "env": {"result": true}},
  {"agent": {"tool": "query", "input": "aab"}, "env": {"result": true}},
  {"agent": {"tool": "query", "input": "abb"}, "env": {"result": false}},
  {"agent": {"tool": "query", "input": "ba"}, "env": {"result": false}},
  {
    "agent": {
      "tool": "submit",
      "dfa": {
        "states": ["s0", "s1", "s2"],
        "start": "s0",
        "accept": ["s2"],
        "delta": {
          "s0,a": "s1",
          "s0,b": "s0",
          "s1,a": "s1",
          "s1,b": "s2",
          "s2,a": "s1",
          "s2,b": "s0"
        }
      }
    },
    "env": {
      "equivalent": true,
      "num_queries": 5,
      "reward": 0.99
    }
  }
]
```

**Grading note.** The submitted DFA is alpha-renamed but equivalent to the hidden DFA. With `EPS=0.002`, reward is `1.0 - 0.002 * 5 = 0.99`. If the submission accepted `"abb"`, product-automaton BFS would return a distinguishing string such as `"abb"` and `equivalent=false`.

### Example C1: Family C, Boolean junta induction

**Hidden oracle (not shown to agent).** Inputs are bit vectors of length 6. The target depends only on bits 0, 2, and 4:

```python
def f(x):
    return int((x[0] and not x[2]) ^ bool(x[4]))
```

**Initial observation shown to agent.**

```json
{
  "family": "boolean_junta",
  "signature": "f: {0,1}^6 -> {0,1}",
  "n_bits": 6,
  "probe_budget": 10,
  "actions": ["query", "submit"],
  "submission_format": "boolean expression AST over variables x0..x5"
}
```

**One active transcript.**

```json
[
  {"agent": {"tool": "query", "input": [0,0,0,0,0,0]}, "env": {"result": 0}},
  {"agent": {"tool": "query", "input": [1,0,0,0,0,0]}, "env": {"result": 1}},
  {"agent": {"tool": "query", "input": [1,0,1,0,0,0]}, "env": {"result": 0}},
  {"agent": {"tool": "query", "input": [0,0,0,0,1,0]}, "env": {"result": 1}},
  {"agent": {"tool": "query", "input": [1,0,0,0,1,0]}, "env": {"result": 0}},
  {
    "agent": {
      "tool": "submit",
      "expr": {
        "op": "xor",
        "args": [
          {"op": "and", "args": [{"var": "x0"}, {"op": "not", "arg": {"var": "x2"}}]},
          {"var": "x4"}
        ]
      }
    },
    "env": {
      "equivalent": true,
      "num_queries": 5,
      "reward": 0.99
    }
  }
]
```

**Why this tests active probing.** The second query isolates bit 0, the third checks whether bit 2 gates bit 0, and the fourth/fifth identify the XOR interaction with bit 4. A passive baseline that receives random examples may need many more samples before seeing the interaction.

### Example B1: Family B, bounded DSL induction

This is the Phase-2 rigorous version: both hidden program and submission are DSL ASTs, not arbitrary Python.

**Bounded domain.**

```json
{
  "input_type": "list[int]",
  "max_len": 8,
  "value_range": [-5, 5]
}
```

**Hidden oracle (not shown to agent).** Keep the even numbers, multiply each by 2, then reverse the result.

```json
{
  "family": "bounded_dsl",
  "task_id": "dsl_filter_map_reverse_0001",
  "hidden_ast": {
    "op": "reverse",
    "arg": {
      "op": "map",
      "fn": {"op": "mul_const", "c": 2},
      "arg": {
        "op": "filter",
        "pred": {"op": "is_even"},
        "arg": {"op": "input"}
      }
    }
  }
}
```

**Initial observation shown to agent.**

```json
{
  "family": "bounded_dsl",
  "signature": "f: list[int] -> list[int]",
  "domain": {"max_len": 8, "value_range": [-5, 5]},
  "probe_budget": 12,
  "actions": ["query", "submit"],
  "allowed_ops": ["input", "filter", "map", "reverse", "take", "drop", "running_sum"],
  "submission_format": "DSL AST"
}
```

**One active transcript.**

```json
[
  {"agent": {"tool": "query", "input": [1,2,3,4]}, "env": {"result": [8,4]}},
  {"agent": {"tool": "query", "input": [4,2]}, "env": {"result": [4,8]}},
  {"agent": {"tool": "query", "input": [-2,-1,0,3]}, "env": {"result": [0,-4]}},
  {"agent": {"tool": "query", "input": []}, "env": {"result": []}},
  {
    "agent": {
      "tool": "submit",
      "ast": {
        "op": "reverse",
        "arg": {
          "op": "map",
          "fn": {"op": "mul_const", "c": 2},
          "arg": {
            "op": "filter",
            "pred": {"op": "is_even"},
            "arg": {"op": "input"}
          }
        }
      }
    },
    "env": {
      "equivalent": true,
      "equivalence_method": "exhaustive bounded enumeration",
      "num_queries": 4,
      "reward": 0.992
    }
  }
]
```

**Near-miss caught by active probing.** The first query alone is consistent with "filter evens, double them" and "filter evens, double them, reverse." The second query `[4,2] -> [4,8]` distinguishes the reverse from the non-reverse version.

### Example D1: Family D, terminal mystery-binary

This family is intentionally fuzz-graded and should remain outside the core claim.

**Hidden script (not shown to agent).**

```python
import json
import sys

def transform(x):
    if not isinstance(x, list):
        return []
    out = []
    running = 0
    for v in x:
        if isinstance(v, int):
            running += v
            if running % 2 == 0:
                out.append(running)
    return out

try:
    value = json.loads(sys.stdin.readline())
    print(json.dumps(transform(value)))
except Exception:
    print(json.dumps([]))
```

**Initial observation shown to agent.**

```json
{
  "family": "terminal_binary",
  "signature": "stdin JSON value -> stdout JSON value",
  "probe_budget": 15,
  "actions": ["query", "submit"],
  "submission_format": "Python source implementing transform(x)",
  "grading": "fuzz equivalence on fresh random and adversarial inputs"
}
```

**One active transcript.**

```json
[
  {"agent": {"tool": "query", "input": [1,1,1]}, "env": {"stdout": "[2]"}},
  {"agent": {"tool": "query", "input": [2,3,1]}, "env": {"stdout": "[2,6]"}},
  {"agent": {"tool": "query", "input": [-1,1,2]}, "env": {"stdout": "[0,2]"}},
  {"agent": {"tool": "query", "input": "abc"}, "env": {"stdout": "[]"}},
  {
    "agent": {
      "tool": "submit",
      "code": "def transform(x):\n    if not isinstance(x, list):\n        return []\n    out = []\n    running = 0\n    for v in x:\n        if isinstance(v, int):\n            running += v\n            if running % 2 == 0:\n                out.append(running)\n    return out\n"
    },
    "env": {
      "fuzz_pass_rate": 1.0,
      "num_queries": 4,
      "reward": 0.992,
      "note": "Probabilistic pass, not an exact equivalence proof."
    }
  }
]
```

### Example evaluation row

A final report should include rows at this level of granularity before aggregating.

```json
{
  "model": "qwen3-8b-active-rl",
  "split": "heldout_phase1",
  "family": "automata",
  "tier": "easy",
  "task_id": "dfa_ends_with_ab_easy_0001",
  "correct": true,
  "num_queries": 5,
  "probe_budget": 8,
  "reward": 0.99,
  "shortest_counterexample_if_wrong": null,
  "baseline_passive_correct": false,
  "base_model_correct": false
}
```
