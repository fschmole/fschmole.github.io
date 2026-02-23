---
layout: post
title: "Machine-Readable Specifications: The Single Source of Truth for AI-Augmented Hardware Design"
date: 2026-02-16 14:00:00 -0800
categories: [Architecture]
tags: [specifications, tla+, ai, rtl, formal-methods, fabric]
toc: true
mermaid: true
---

Every hardware team has lived this: a 400-page PDF spec says one thing, the
RTL says another, and the testbench assumes a third.  The bug that falls out
is nobody's fault and everybody's problem.  Now multiply that failure mode by
an LLM that has no judgment about which source to trust — and "making
something up" becomes the default behavior whenever the input is ambiguous.

If we are serious about AI-augmented hardware design, we need to fix the
input before we fix the model.

## Ease of Consumption — Not Just for Humans

Architectural specifications have historically been written for humans.
They are prose documents — Word files, Confluence pages, PDFs — optimized
for readability by an engineer who already has context.  That works (barely)
when the consumer is a person who can resolve ambiguity by walking to the
next cubicle.

It does not work when the consumer is an LLM.

Large language models are *extremely* sensitive to the quality of their
input.  Give an LLM a clean, unambiguous, machine-readable rule set and it
will generate correct RTL, accurate testbench stimulus, and valid
configuration sequences.  Give it a vague paragraph with an implicit
cross-reference to a table four sections away and it will *hallucinate
plausible-looking logic that is wrong*.

The problem is not the model.  The problem is the specification.

## The Single Source of Truth

The fix is a **machine-readable golden source** — a structured, formal
representation of the design's rules and behaviors from which *everything
else* is derived.  Not "also maintained alongside the PDF," but the actual
source of record.

```mermaid
flowchart TD
    subgraph legacy["Legacy Corpus (existing specs)"]
        direction TB
        PDF_OLD["PDF Specs"]
        WORD_OLD["Word / Confluence Docs"]
        PG_OLD["Programmer's Guides"]
    end

    subgraph conversion["Conversion & Verification"]
        direction TB
        LLM_CONVERT["LLM-Assisted<br/>Conversion"]
        MANUAL_REVIEW["Manual Review<br/>& Reconciliation"]
        RTL_VERIFY["Verify Against<br/>Existing RTL<br/>(true golden ref)"]
    end

    subgraph golden["Machine-Readable Golden Source"]
        direction TB
        TLA["TLA+ / PlusCal<br/>(behavioral rules)"]
        STRUCT["XML / YAML / JSON<br/>(registers, fields,<br/>address maps)"]
    end

    subgraph consumers["Downstream Consumers"]
        direction TB
        HUMAN_SPEC["Human-Readable Specs<br/>(auto-generated PDF,<br/>Markdown, HTML)"]
        WEB_APP["Interactive Web Apps<br/>(pre-indexed search,<br/>cross-referenced<br/>register browser)"]
        AI_FLOW["AI-Augmented Flows<br/>(RTL generation,<br/>testbench synthesis,<br/>assertion extraction)"]
    end

    PDF_OLD -. "LLM ingestion" .-> LLM_CONVERT
    WORD_OLD -. "LLM ingestion" .-> LLM_CONVERT
    PG_OLD -. "LLM ingestion" .-> LLM_CONVERT
    LLM_CONVERT --> MANUAL_REVIEW
    MANUAL_REVIEW --> RTL_VERIFY
    RTL_VERIFY -. "reconciled & validated" .-> golden

    golden ==> HUMAN_SPEC
    golden ==> WEB_APP
    golden ==> AI_FLOW
```

The thick arrows from the golden source are the steady-state flow: every
consumer reads from the same canonical data.  The dashed lines on the left
represent the *one-time migration* — the up-front work required to get there.

## Why Formal Modeling Matters for Fabrics

An I/O-memory fabric is governed by rules: ordering constraints, credit
protocols, arbitration policies, coherence state transitions, deadlock
freedom invariants.  These are not well captured by prose.  They *are* well
captured by temporal logic.

**TLA+** (Temporal Logic of Actions) and its procedural alias **PlusCal**
let you express exactly these kinds of rules:

- *"A posted write must not pass a completion with the same requester ID."*
- *"Credits are returned only after the receiver has consumed the
  corresponding data."*
- *"No reachable state exists in which two agents hold exclusive ownership
  of the same cache line."*

A TLA+ specification is simultaneously:

1. **Precise enough for a model checker** (TLC) to exhaustively verify.
2. **Readable enough for a human** to review the intent.
3. **Structured enough for an LLM** to consume without ambiguity.

That last property is the one most teams overlook.  When the fabric's
ordering rules live in a formal spec, an LLM generating RTL for an arbiter
or a reorder buffer can be given the *exact* invariants it must satisfy —
not a paragraph of English that it might misinterpret.

## The Migration Path

None of this is free.  For a team with an existing design, the path looks
roughly like this:

### Step 1 — Convert the existing corpus

Take every PDF spec, programmer's guide, and architecture note and convert
it into machine-readable form (structured YAML/JSON for register maps,
TLA+ for behavioral rules).

This is where LLMs can actually help *today*.  Feed the prose documents
into a well-prompted model and let it produce a first-draft structured
output.  But — and this is critical — **every generated artifact must be
manually reviewed**.  LLMs are good at format conversion; they are not
reliable at semantic interpretation of ambiguous prose.

### Step 2 — Verify against the existing RTL

The existing RTL is the *true* golden reference (it is, after all, what the
silicon actually does).  Use it to validate the converted specs:

- Run the TLA+ model checker against properties extracted from the RTL.
- Diff the machine-readable register maps against the RTL's CSR decoder.
- Flag every discrepancy — these are either spec bugs, RTL bugs, or both.

This step is painful but enormously valuable.  Teams that have done it
invariably discover long-standing bugs hiding in the gap between the spec
and the implementation.

### Step 3 — Flip the flow

Once the golden source is validated, *stop editing the PDFs directly*.
All changes start in the machine-readable source.  Human-readable documents,
interactive tools, and AI pipelines all consume from the same root.

## Interactive Specifications

A machine-readable golden source enables a class of tooling that PDFs
simply cannot support: **interactive, pre-indexed, cross-referenced
specification browsers**.

Imagine a web app where an engineer can:

- Search across *all* specs simultaneously with structured filters
  (e.g. "show me every register in the fabric's credit manager that has
  a reset value other than zero").
- Click a register field and immediately see every ordering rule, every
  TLA+ invariant, and every testbench sequence that touches it.
- Get answers in seconds instead of grep-ing through a dozen PDFs.

This is not speculative.  It is a straightforward engineering project once
the data is structured.

### A Concrete Example: Generated CSR Documentation

To make this tangible, I built a Python script that parses a
machine-readable register specification (XML-based) and generates a
fully self-contained, interactive HTML documentation site — no server,
no database, just static files you can open in a browser or host on an
internal web server.  The golden source is an XML description of every
control/status register: address maps, register instances, bit-field
definitions, reset values, access policies, and cross-references.  The
script consumes that XML and produces a set of interlinked HTML pages.

Here is what the generated output provides:

**Global search with pre-built index.**  At build time, the script
constructs a JSON search index covering every register and every
bit-field — name, description, address map context — and embeds it
directly in the HTML.  The search modal (triggered by clicking the
floating search button or pressing `/`) performs instant client-side
substring matching against the pre-computed index.  Results are
categorized with colored chips (Register vs. Bitfield), show context
about which address-map instance they belong to, and link directly to
the relevant detail section.  No server round-trip, no waiting — up to
75 results appear as you type.

**Filter-as-you-type on every table.**  Each register summary table has
a sticky search bar with a frosted-glass backdrop that filters rows
live on every keystroke, matching against any column.  On the top-level
index page, separate filter inputs cover address-map instances and
logical interfaces independently.

**Visual bit-field diagrams.**  Every register is rendered as an
HTML table where each column is one bit.  Three rows show bit numbers
(MSB to LSB), default/reset values (`0`, `1`, `?`, or `—`), and
field names — with multi-bit fields merged via `colspan` and labels
rotated vertically so they remain readable even in narrow columns.
Fields alternate between two blue shades for a zebra-stripe effect;
reserved bits are gray; bits beyond the register width are dimmed.

**Keyboard shortcuts.**  `/` opens search, `C` toggles compact mode
(smaller fonts, fewer columns — useful on laptops), `S` toggles the
interface summary panel, `T` scrolls to top.  All suppressed when
focus is in an input field.

**Rich register detail cards.**  Each register gets its own expandable
section with: short and long descriptions, a metadata grid (modules,
consumers, access-policy badges), an instances table with computed
absolute addresses per interface exposure, the bit-field diagram, and
a full bit-field table with access type, reset values, and
hardware-load cross-references rendered as dot-separated paths that
link to the referenced register.

**Deep linking with copy-to-clipboard.**  Every register detail section
has a stable URL anchor (name + content hash for uniqueness) and a
"Copy link" button that writes the full URL to the clipboard with
visual feedback.  Engineers can paste direct links into bug reports or
chat messages — the recipient lands exactly on the right register,
not on page 1 of a 400-page PDF.

**Compact mode with persistence.**  The compact toggle shrinks fonts
and hides verbose columns (description, address-map name, register
width) to fit more registers on screen.  The preference is saved to
`localStorage` and restored on next visit.

**Zero runtime dependencies.**  The generated HTML files are fully
self-contained — CSS and JavaScript are inlined.  They can be opened
from a file share, served from a minimal web server, or embedded in
a CI artifact.  No frameworks, no build step, no node_modules.

The point is not the specific tool — it is the *pattern*.  Once the
register specification lives in a structured, machine-readable format,
building this kind of interactive, searchable, deeply-linked
documentation is a weekend project.  Doing the same thing from a PDF
is effectively impossible.

## The Up-Front Cost and the Payoff

Let's be honest: the up-front work is significant.  Converting a mature
design's specification corpus into machine-readable form is a
multi-quarter effort, even with LLM assistance.  It requires
domain experts reviewing every conversion, resolving every ambiguity,
and reconciling every spec-vs-RTL discrepancy.

The payoff is equally significant:

- **AI-augmented RTL generation** becomes viable because the input is
  unambiguous.
- **Spec-RTL drift** becomes structurally impossible — the spec *is* the
  input to the toolchain.
- **Onboarding time** drops dramatically when new engineers can search
  and browse instead of reading binders.
- **Bug density** decreases because the formal model catches classes of
  errors (ordering violations, deadlocks, credit leaks) before any RTL
  is written.

The teams that begin this migration now will have a compounding advantage
over those that wait.  The cost of conversion is fixed; the cost of
*not* converting grows with every generation of AI tooling that could
have consumed the spec but couldn't because it was trapped in a PDF.
