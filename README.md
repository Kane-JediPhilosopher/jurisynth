# Jurisynth: A Neuro-Symbolic Legal AI Assistant with Explicit Reasoning

Hi, I’m Kane 🤘 — this repository contains my thesis project, *Jurisynth*, a neuro-symbolic AI assistant designed to support structured and interpretable legal reasoning.

---

## Overview

Jurisynth combines large language models (LLMs) with a knowledge graph (KG) and explicit reasoning traces to improve how AI systems handle legal information.

- The **“neuro”** component refers to LLM-based multi-agent reasoning  
- The **“symbolic”** component refers to a knowledge graph representing structured legal knowledge  
- The **reasoning log** provides an explicit record of intermediate steps for inspection and verification  

The goal is to explore how these components can work together to improve grounding, comprehensiveness, and auditability in legal reasoning tasks.

---

## Motivation

Large language models are capable of generating fluent and contextually relevant responses, but they are also prone to issues such as hallucinations, limited context windows, and lack of explicit verifiability.

In high-stakes domains like law, these limitations become especially important. Legal decision-making requires not only plausible reasoning, but also traceable and defensible conclusions.

At the same time, legal professionals themselves face cognitive limitations, including working memory constraints and susceptibility to cognitive biases.

This motivates the question:

> How can we design AI systems that support more reliable, structured, and inspectable reasoning in legal contexts?

---

## System Architecture

Jurisynth is built around three main components:

- **Multi-Agent Network**  
  A set of LLM-based agents that decompose tasks, retrieve information, and synthesise responses.

- **Knowledge Graph (KG)**  
  A structured representation of legal entities and relationships, used to ground reasoning in explicit data.

- **Reasoning Log**  
  A trace of intermediate reasoning steps that supports inspection, debugging, and verification of outputs.

Together, these components aim to balance flexible language-based reasoning with structured symbolic constraints.

---

## What This Project Explores

Rather than focusing on a single algorithmic novelty, this project explores whether combining:
- LLM-based reasoning,
- knowledge graph grounding, and  
- explicit reasoning traces  

can improve the **reliability and interpretability** of AI-assisted legal reasoning.

More broadly, rather than a loosely coupled integration of LLM reasoning, knowledge graph querying, and reasoning traces, I am interested in introducing connective mechanisms that enable tighter interaction between neural and symbolic components within the reasoning process.

In particular, this includes exploring whether lightweight symbolic (post-hoc) validation mechanisms, integrated into the system’s orchestration layer, can meaningfully improve the reliability of LLM reasoning in structured settings.

---

## Context

Systems such as RAG and GraphRAG have explored ways of grounding LLM outputs using external data sources. More recently, multi-agent and neuro-symbolic approaches have become increasingly common in research literature (e.g., arXiv, 2025–2026).

Jurisynth sits within this general direction, but focuses specifically on:
- tighter integration with a knowledge graph for structured grounding  
- explicit reasoning traces for auditability and inspection  
- a multi-agent design for decomposition and synthesis of reasoning tasks  

---

## Status

Work in progress (thesis project, 2025–2026).

---

## Notes

This project is exploratory in nature and focuses on system design rather than large-scale deployment or production-level optimisation. The emphasis is on interpretability, structure, and reasoning transparency rather than raw model performance.

---

## Installation (TODO)

<!--
- Requirements
- Setup steps
- Environment configuration
-->

---

## Usage (TODO)

<!--
- Example commands
- Sample inputs/outputs
- How to run the system end-to-end
-->

---

## Example Output (TODO)

<!--
- Show a sample query
- Show reasoning trace
- Show final answer
-->

---

## Project Structure (TODO)

<!--
- Explain key folders/files
-->

---

## Limitations (TODO)

<!--
- Known weaknesses
- Failure cases
- Scope boundaries
-->

---

## Future Work (TODO)

<!--
- Planned improvements
- Research directions
-->

---

## Status

Work in progress (thesis project, 2025–2026).