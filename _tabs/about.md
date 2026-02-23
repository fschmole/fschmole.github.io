---
# the default layout is 'page'
icon: fas fa-user-circle
order: 1
---

# About

I'm a **silicon SoC, IP, and I/O architect** with 25+ years of experience
specializing in high-performance interconnects (PCIe/CXL/UXI), coherency,
and scalability.  I've spent my career at the boundary between architectural
intent and silicon reality — defining fabric protocols, proving them correct,
and making sure the RTL does what the spec says.

## Architectural Philosophy

I believe in **correct-by-construction** silicon.  That means:

- **Data over intuition.**  Architectural decisions should be grounded in
  trace analysis, first-principles modeling, and exhaustive formal
  verification — not gut feel and hallway consensus.
- **Machine-readable specifications.**  Prose specs accumulate ambiguity.
  I advocate for code-as-spec workflows (TLA+/PlusCal, XML/YAML/JSON,
  PlantUML) where the specification is *executable*, *model-checkable*,
  and precise enough for both humans and LLMs to consume without
  guesswork.
- **Single source of truth.**  Every downstream artifact — human-readable
  docs, interactive tools, RTL, testbenches — should be generated from
  the same golden source.  Spec-RTL drift is not a fact of life; it is
  a process failure.
- **Spec-to-prompt precision.**  As AI-augmented design becomes the norm,
  the quality of the specification *is* the quality of the output.
  Ambiguity in the input is hallucination in the result.

## Core Competencies

| Domain | Details |
|---|---|
| **Interconnect Architecture** | PCIe Gen6/7, CXL, UXI, SoC fabric design, caching & coherency |
| **I/O Virtualization** | VT-d, Intel VMD / Virtual Meta Device, device aggregation for rack-scale AI |
| **Formal Methods** | PlusCal/TLA+ modeling, TLC model checking, deadlock analysis, invariant proofs |
| **Data-Driven Verification** | Python trace modeling, PCIe/CXL trace analysis, bandwidth simulation |
| **Methodology & Tooling** | Machine-readable documentation, code-as-spec, interactive spec browsers |
| **Technical Leadership** | Specification governance, cross-functional alignment, mentorship |

## Select Technical Wins

- **GPU Interconnect Optimization** — Led architectural discovery for PCIe
  P2P ordering enhancements. Identified and resolved a critical
  destination-change stall, enabling a ~2000% gain in nvbandwidth benchmarks
  for multi-agent GPU clusters while maintaining same-address ordering.
- **Mesh Architecture Efficiency** — Optimized mesh topology and protocol,
  reducing power consumption and alleviating oversubscription.
- **Latency Reduction** — Developed firmware-based custom multicast routing
  through the CPU, dramatically reducing latency, power, and platform cost for storage customers, leading to important design wins and customer retention. 
- **Virtual Meta Device** — Re-architected the legacy Volume Management
  Device into a strategic scalability solution for server platforms,
  enabling virtualized storage and networking aggregation.
- **15 USPTO patent filings** and 27 invention disclosures focused on
  interconnects, coherency, and virtualization.

## Education

- **M.S., Electrical and Computer Engineering** — Georgia Institute of
  Technology 
    - Minor in Economics and Game Theory
    - Teaching assistant in Microcotroller-Based Design
- **B.S., Electrical Engineering** — Georgia Institute of
  Technology 
    - Teaching assistant in Calculus IV

## Elsewhere

- [GitHub](https://github.com/fschmole) — public scripts and tools
- [LinkedIn](https://www.linkedin.com/in/filipschmole)

## About This Site

Posts here cover hardware architecture, design, and verification, including
the tools I build to make hardware design faster and more rigorous. Written
for engineers who work in or adjacent to silicon design.

## Contact

<style>
  .about-contact-form input,
  .about-contact-form textarea {
    width: 100%;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.5rem;
    border: 1px solid var(--border-color, #d0d0d0);
    border-radius: 0.375rem;
    background: var(--card-bg, var(--main-bg, #fff));
    color: var(--text-color, var(--body-color, #212529));
    font-size: 0.95rem;
    font-family: inherit;
    box-sizing: border-box;
  }
  .about-contact-form input::placeholder,
  .about-contact-form textarea::placeholder {
    color: var(--text-muted-color, #6c757d);
    opacity: 0.7;
  }
  .about-contact-form input:focus,
  .about-contact-form textarea:focus {
    outline: none;
    border-color: var(--link-color, #0a5ad4);
    box-shadow: 0 0 0 2px rgba(10, 90, 212, 0.15);
  }
  .about-contact-form button {
    padding: 0.5rem 1.5rem;
    border: 1px solid var(--link-color, #0a5ad4);
    border-radius: 0.375rem;
    background: transparent;
    color: var(--link-color, #0a5ad4);
    font-size: 0.95rem;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
  }
  .about-contact-form button:hover {
    background: var(--link-color, #0a5ad4);
    color: #fff;
  }
</style>

<form action="https://formspree.io/f/meelprqp" method="POST" class="about-contact-form" style="max-width: 480px;">
  <input type="text" name="name" placeholder="Name (optional)">
  <input type="email" name="email" placeholder="Email" required>
  <textarea name="message" placeholder="Message" required rows="4"></textarea>
  <input type="hidden" name="_subject" value="schmole.com — contact form">
  <button type="submit">Send</button>
</form>
