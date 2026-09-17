"""Strict JSON-schema contracts for every structured Agentic Reasoner LLM turn."""

from __future__ import annotations


def schema(name: str, body: dict[str, object]) -> dict[str, object]:
    return {"name": name, "strict": True, "schema": body}


TASK_ANALYSIS_SCHEMA = schema("task_analysis", {
    "type": "object", "properties": {
        "route": {"type": "string", "enum": ["direct", "complex"]},
        "contextual_facts": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "object", "additionalProperties": True},
    }, "required": ["route", "contextual_facts", "constraints"], "additionalProperties": False,
})

INTAKE_SCHEMA = schema("conversation_intake", {
    "type": "object", "properties": {
        "action": {"type": "string", "enum": ["proceed", "clarify"]},
        "contextual_facts": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "object", "additionalProperties": True},
        "clarification_question": {"type": ["string", "null"]},
    }, "required": ["action", "contextual_facts", "constraints", "clarification_question"], "additionalProperties": False,
})

REQUEST_ANALYSIS_SCHEMA = schema("request_analysis", {
    "type": "object", "properties": {
        "action": {"type": "string", "enum": ["proceed", "clarify"]},
        "route": {"type": "string", "enum": ["direct", "complex"]},
        "contextual_facts": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "object", "additionalProperties": True},
        "clarification_question": {"type": ["string", "null"]},
    }, "required": ["action", "route", "contextual_facts", "constraints", "clarification_question"],
    "additionalProperties": False,
})

DEPENDENCY_SCHEMA = schema("semantic_dependencies", {
    "type": "object", "properties": {
        "dependencies": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
    }, "required": ["dependencies"], "additionalProperties": False,
})

LEAF_ANSWER_SCHEMA = schema("evidence_grounded_leaf_answer", {
    "type": "object", "properties": {
        "status": {"type": "string", "enum": ["supported", "partially_supported", "insufficient_evidence"]},
        "answer_text": {"type": "string"},
        "claims": {"type": "array", "items": {"type": "object", "properties": {
            "text": {"type": "string"},
            "evidence_refs": {"type": "array", "items": {"type": "string"}},
            "status": {"type": "string", "enum": ["supported", "partially_supported", "insufficient_evidence"]},
        }, "required": ["text", "evidence_refs", "status"], "additionalProperties": False}},
    }, "required": ["status", "answer_text", "claims"], "additionalProperties": False,
})

REPORT_SCHEMA = schema("final_report", {
    "type": "object", "properties": {
        "overview": {"type": "string"},
        "sections": {"type": "array", "items": {"$ref": "#/$defs/section"}},
        "contradiction_refs": {"type": "array", "items": {"type": "string"}},
    }, "required": ["overview", "sections", "contradiction_refs"], "additionalProperties": False,
    "$defs": {"section": {"type": "object", "properties": {
        "section_id": {"type": "string"}, "title": {"type": "string"}, "answer_text": {"type": "string"},
        "claim_refs": {"type": "array", "items": {"type": "string"}},
        "child_sections": {"type": "array", "items": {"$ref": "#/$defs/section"}},
    }, "required": ["section_id", "title", "answer_text", "claim_refs", "child_sections"], "additionalProperties": False}},
})

QCOMPILER_SCHEMA = schema("qcompiler_expression", {
    "type": "object", "properties": {"expression": {"type": "string"}},
    "required": ["expression"], "additionalProperties": False,
})

QCOMPILER_AST_SCHEMA = schema("qcompiler_ast", {
    "type": "object", "properties": {"ast": {"$ref": "#/$defs/node"}},
    "required": ["ast"], "additionalProperties": False,
    "$defs": {"node": {"anyOf": [
        {"type": "object", "properties": {
            "type": {"type": "string", "enum": ["query"]}, "query": {"type": "string"},
        }, "required": ["type", "query"], "additionalProperties": False},
        {"type": "object", "properties": {
            "type": {"type": "string", "enum": ["parallel"]},
            "children": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/node"}},
        }, "required": ["type", "children"], "additionalProperties": False},
        {"type": "object", "properties": {
            "type": {"type": "string", "enum": ["dependent"]},
            "left": {"$ref": "#/$defs/node"}, "right": {"$ref": "#/$defs/node"},
        }, "required": ["type", "left", "right"], "additionalProperties": False},
    ]}},
})

CONTRADICTION_EXPLANATION_SCHEMA = schema("contradiction_explanations", {
    "type": "object", "properties": {
        "explanations": {"type": "array", "items": {"type": "object", "properties": {
            "contradiction_id": {"type": "string"},
            "explanation": {"type": "string"},
        }, "required": ["contradiction_id", "explanation"], "additionalProperties": False}},
    }, "required": ["explanations"], "additionalProperties": False,
})

QUERY_INTERPRETER_SCHEMA = schema("retrieval_concepts", {
    "type": "object", "properties": {
        "entity_concepts": {"type": "array", "items": {"$ref": "#/$defs/concept"}},
        "relation_concepts": {"type": "array", "items": {"$ref": "#/$defs/concept"}},
    }, "required": ["entity_concepts", "relation_concepts"], "additionalProperties": False,
    "$defs": {"concept": {"type": "object", "properties": {
        "concept": {"type": "string"},
        "variants": {"type": "array", "items": {"type": "string"}},
    }, "required": ["concept", "variants"], "additionalProperties": False}},
})
