import openai
import os
import json
import rdflib
import time

# Retrieve API keys securely
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

# For testing
openai.api_key  = os.getenv('OPENAI_API_KEY')

RECEPTIONIST_KEY = os.getenv('RECEPTIONIST')
EVALUATOR_KEY = os.getenv('EVALUATOR')

practice_areas = [
    "Bankruptcy and insolvency law",
    "Commercial law",
    "Consumer law",
    "Criminal law",
    "Employment law",
    "EU law",
    "Family law",
    "Human rights and civil liberties",
    "Immigration and asylum law",
    "Intellectual property",
    "Information Technology (IT) law",
    "Litigation, mediation, arbitration",
    "Personal injury, damage to goods",
    "Property law",
    "Public law",
    "Social security law",
    "Succession law",
    "Tax law",
    "Traffic and transport law"
]

EXPERT_KEYS = {
    "Bankruptcy and insolvency law": os.getenv('BANKRUPTCY_INSOLVENCY'),
    "Commercial law": os.getenv('COMMERCIAL'),
    "Consumer law": os.getenv('CONSUMER'),
    "Criminal law": os.getenv('CRIMINAL'),
    "Employment law": os.getenv('EMPLOYMENT'),
    "EU law": os.getenv('EU'),
    "Family law": os.getenv('FAMILY'),
    "Human rights and civil liberties": os.getenv('HUMAN_RIGHTS_CIVIL_LIBERTIES'),
    "Immigration and asylum law": os.getenv('IMMIGRATION_ASYLUM'),
    "Intellectual property": os.getenv('IP'),
    "Information Technology (IT) law": os.getenv('IT'),
    "Litigation, mediation, arbitration": os.getenv('LITIGATION_MEDIATION_ARBITRATION'),
    "Personal injury, damage to goods": os.getenv('PERSONAL_INJURY_DAMAGE_TO_GOODS'),
    "Property law": os.getenv('PROPERTY'),
    "Public law": os.getenv('PUBLIC_LAW'),
    "Social security law": os.getenv('SOCIAL_SECURITY'),
    "Succession law": os.getenv('SUCCESSION'),
    "Tax law": os.getenv('TAX'),
    "Traffic and transport law": os.getenv('TRAFFIC_TRANSPORT')
}

eu_graph = rdflib.Dataset().parse("eu_legislation_graph.nq", format="nquads")

class Legal_Agent:
    def __init__(self, system_prompt="", step_prompts=[], api_key="", tool_table=dict()):
        self.system_prompt = system_prompt
        self.step_prompts = step_prompts
        self.context = [{"role": "system", "content": system_prompt}]
        self.reasoning_log = []
        self.tool_lookup = {value['function']['name']: func for func, value in tool_table.items()}
        self.tools = [value for value in tool_table.values()]
        self.api_key = api_key
        self.instance = openai.OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        print(f"[INIT] Legal_Agent initialized.")
        print(f"[INIT] Tools registered: {list(self.tool_lookup.keys())}")
        print(f"[INIT] Step prompts loaded: {len(self.step_prompts)}")

    # -------------------------------------------------------------------------
    # Core response method (non-streaming)
    # -------------------------------------------------------------------------
    def respond_to(self, query="", role="user", _depth=0):
        indent = "  " * _depth  # Indent nested (tool-loop) calls for readability

        if query:
            print(f"{indent}[RESPOND] Appending {role} message ({len(query)} chars)")
            self.context.append({"role": role, "content": query})

        print(f"{indent}[RESPOND] Sending request to model "
              f"(context length: {len(self.context)} messages)...")
        t0 = time.perf_counter()

        answer = self.instance.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="high",
            messages=self.context,
            temperature=0,
            top_p=0.1,
            tools=self.tools,
            max_tokens=None,
            stream=False
        )

        elapsed = time.perf_counter() - t0
        print(f"{indent}[RESPOND] Model responded in {elapsed:.2f}s | "
              f"finish_reason={answer.choices[0].finish_reason} | "
              f"usage={answer.usage}")

        reasoning = getattr(answer.choices[0].message, "reasoning_content", None)
        if reasoning:
            print(f"{indent}[REASONING] {str(reasoning)[:200]}{'...' if len(str(reasoning)) > 200 else ''}")
        self.reasoning_log.append(str(reasoning))

        # --- Tool call branch ---
        if answer.choices[0].message.tool_calls:
            tool_call  = answer.choices[0].message.tool_calls[0]
            tool_name  = tool_call.function.name
            args       = json.loads(tool_call.function.arguments)

            print(f"{indent}[TOOL] Calling '{tool_name}' with args: {args}")

            self.context.append(answer.choices[0].message)

            if tool_name not in self.tool_lookup:
                raise KeyError(f"[TOOL] Unknown tool requested by model: '{tool_name}'")

            t1 = time.perf_counter()
            tool_result = self.tool_lookup[tool_name](
                **args,
                api_key=self.api_key
                )
            tool_elapsed = time.perf_counter() - t1

            result_preview = str(tool_result)[:300]
            print(f"{indent}[TOOL] '{tool_name}' returned in {tool_elapsed:.2f}s: "
                  f"{result_preview}{'...' if len(str(tool_result)) > 300 else ''}")

            self.context.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": str(tool_result)
            })

            print(f"{indent}[TOOL] Re-entering respond_to (depth {_depth + 1})...")
            return self.respond_to(_depth=_depth + 1)

        # --- Normal response branch ---
        content = answer.choices[0].message.content
        print(f"{indent}[RESPOND] Final answer ({len(content)} chars): "
              f"{content[:150]}{'...' if len(content) > 150 else ''}")

        self.context.append({"role": "assistant", "content": content})
        return content


    # -------------------------------------------------------------------------
    # Streaming response method
    # -------------------------------------------------------------------------
    def stream(self, query="", role="user", on_chunk=None):
        """
        Stream a response from the model, yielding text chunks as they arrive.

        Args:
            query    : The user message to send (appended to context if non-empty).
            role     : Role for the message (default "user").
            on_chunk : Optional callback(chunk_str) called on every text chunk.

        Yields:
            str: Individual text delta chunks from the model.

        Note: Tool calls are NOT supported in streaming mode here. If the model
        decides to call a tool mid-stream, a NotImplementedError is raised — use
        respond_to() for tool-heavy workflows.
        """
        if query:
            print(f"[STREAM] Appending {role} message ({len(query)} chars)")
            self.context.append({"role": role, "content": query})

        print(f"[STREAM] Opening stream "
              f"(context length: {len(self.context)} messages)...")
        t0 = time.perf_counter()

        stream = self.instance.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="high",
            messages=self.context,
            temperature=0,
            top_p=0.1,
            tools=self.tools,
            max_tokens=None,
            stream=True                     # <-- streaming enabled
        )

        full_response = []
        chunk_count   = 0
        finish_reason = None

        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None

            # Detect unexpected tool calls in the stream
            if delta and delta.tool_calls:
                raise NotImplementedError(
                    "[STREAM] Model requested a tool call during streaming. "
                    "Use respond_to() instead for tool-enabled workflows."
                )

            if delta and delta.content:
                text = delta.content
                full_response.append(text)
                chunk_count += 1

                if on_chunk:
                    on_chunk(text)

                yield text                  # <-- caller gets each chunk live

            if chunk.choices and chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

        elapsed       = time.perf_counter() - t0
        assembled     = "".join(full_response)

        print(f"[STREAM] Stream complete in {elapsed:.2f}s | "
              f"chunks={chunk_count} | finish_reason={finish_reason} | "
              f"total_chars={len(assembled)}")

        # Persist the assembled reply to context so history stays consistent
        self.context.append({"role": "assistant", "content": assembled})
        print(f"[STREAM] Assembled reply appended to context.")


    def stream_to_string(self, query="", role="user", _depth=0) -> str:
        indent = "  " * _depth

        if query:
            print(f"{indent}[STREAM] Appending {role} message ({len(query)} chars)")
            self.context.append({"role": role, "content": query})

        print(f"{indent}[STREAM] Opening stream (context length: {len(self.context)} messages)...")
        t0 = time.perf_counter()

        response = self.instance.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="high",
            messages=self.context,
            temperature=0,
            top_p=0.1,
            tools=self.tools,
            max_tokens=None,
            stream=True
        )

        full_response = []
        chunk_count   = 0
        finish_reason = None

        tool_call_id  = None
        tool_name_acc = []
        tool_args_acc = []
        is_tool_call  = False
        in_args       = False   # Tracks whether we've started streaming args yet

        print(f"{indent}[STREAM] ", end="", flush=True)

        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None

            if chunk.choices and chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

            # --- Tool call chunks ---
            if delta and delta.tool_calls:
                tc = delta.tool_calls[0]

                # First chunk: tool name arrives — print the call header
                if tc.id:
                    tool_call_id = tc.id
                    is_tool_call = True
                    print()     # Newline to break out of "[STREAM] " prefix line

                if tc.function.name:
                    tool_name_acc.append(tc.function.name)
                    tool_name_so_far = "".join(tool_name_acc)
                    # Reprint the tool header as the name accumulates
                    print(f"\r{indent}[TOOL] Calling '{tool_name_so_far}'...", end="", flush=True)

                if tc.function.arguments:
                    tool_args_acc.append(tc.function.arguments)
                    args_so_far = "".join(tool_args_acc)

                    if not in_args:
                        # First args chunk — start a new args stream line
                        print(f"\n{indent}[TOOL] Args stream: ", end="", flush=True)
                        in_args = True

                    print(args_so_far if not in_args else tc.function.arguments,
                        end="", flush=True)  # Print only the new delta, not full accumulator

                continue

            # --- Normal text chunks ---
            if delta and delta.content:
                if is_tool_call:
                    # Shouldn't happen, but guard anyway
                    print(f"\n{indent}[STREAM] Unexpected text after tool call delta, skipping.")
                    continue

                text = delta.content
                full_response.append(text)
                chunk_count += 1
                print(text, end="", flush=True)

        print()  # Final newline
        elapsed = time.perf_counter() - t0

        # --- Tool call branch ---
        if is_tool_call:
            tool_name = "".join(tool_name_acc)
            tool_args = json.loads("".join(tool_args_acc))

            print(f"{indent}[TOOL] ✓ Stream complete | "
                f"tool='{tool_name}' | args={tool_args}")

            self.context.append({
                "role":    "assistant",
                "content": None,
                "tool_calls": [{
                    "id":       tool_call_id,
                    "type":     "function",
                    "function": {
                        "name":      tool_name,
                        "arguments": "".join(tool_args_acc)
                    }
                }]
            })

            if tool_name not in self.tool_lookup:
                raise KeyError(f"{indent}[TOOL] Unknown tool: '{tool_name}'")

            t1 = time.perf_counter()
            tool_result = self.tool_lookup[tool_name](
                **tool_args,
                api_key=self.api_key
                )
            tool_elapsed = time.perf_counter() - t1

            print(f"{indent}[TOOL] '{tool_name}' returned in {tool_elapsed:.2f}s: "
                f"{str(tool_result)[:300]}{'...' if len(str(tool_result)) > 300 else ''}")

            self.context.append({
                "role":         "tool",
                "tool_call_id": tool_call_id,
                "name":         tool_name,
                "content":      str(tool_result)
            })

            print(f"{indent}[TOOL] Re-entering stream_to_string (depth {_depth + 1})...")
            return self.stream_to_string(_depth=_depth + 1)

        # --- Normal response branch ---
        assembled = "".join(full_response)
        print(f"{indent}[STREAM] Complete in {elapsed:.2f}s | "
            f"chunks={chunk_count} | finish_reason={finish_reason} | "
            f"total_chars={len(assembled)}")

        self.context.append({"role": "assistant", "content": assembled})
        return assembled


    # -------------------------------------------------------------------------
    # Sequential / conditional reasoning (unchanged logic, traces added)
    # -------------------------------------------------------------------------
    def sequential_reasoning(self, query="", max_depth=10):
        print(f"[SEQ] Starting sequential_reasoning | max_depth={max_depth}")
        print(f"[SEQ] Query: {query[:200]}{'...' if len(query) > 200 else ''}")
        state = {"query": query}
        return self.conditional_call(
            step_index=0,
            depth=0,
            max_depth=max_depth,
            state=state
        )

    def conditional_call(self, step_index, depth, max_depth, state):
        print(f"[COND] Step {step_index + 1} | depth={depth}/{max_depth}")

        if depth > max_depth:
            raise RuntimeError(
                f"[COND] Max reasoning depth ({max_depth}) reached at step {step_index + 1}"
            )

        if step_index >= len(self.step_prompts):
            raise IndexError(
                f"[COND] step_index {step_index} out of range "
                f"(only {len(self.step_prompts)} step prompts defined)"
            )

        prompt = self.step_prompts[step_index].format(**state)
        print(f"[COND] Formatted prompt ({len(prompt)} chars): "
              f"{prompt[:150]}{'...' if len(prompt) > 150 else ''}")

        raw_result = self.stream_to_string(prompt, "user")

        try:
            state = json.loads(raw_result)
        except json.JSONDecodeError as e:
            print(f"[COND] ⚠ JSON parse failed: {e}")
            print(f"[COND] Raw result was: {raw_result[:300]}")
            raise

        next_step = state.get("next_step", None)
        print(f"[COND] Step {step_index + 1} complete | next_step={next_step} | "
              f"state keys={list(state.keys())}")

        if next_step is None:
            print(f"[COND] No next_step — sequential reasoning complete.")
            return state

        return self.conditional_call(
            step_index=(next_step - 1),
            depth=(depth + 1),
            max_depth=max_depth,
            state=state
        )

    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    def reset_working_memory(self):
        print("[RESET] Clearing context and reasoning log (full reset).")
        self.context = [{"role": "system", "content": self.system_prompt}]
        self.reasoning_log = []

    def reset_context(self):
        print("[RESET] Clearing context only (reasoning log preserved).")
        self.context = [{"role": "system", "content": self.system_prompt}]

    def export_context(self):
        print(f"[EXPORT] Exporting context ({len(self.context)} messages).")
        return self.context
    
practice_areas = [
    "Bankruptcy and insolvency law",
    "Commercial law",
    "Consumer law",
    "Criminal law",
    "Employment law",
    "EU law",
    "Family law",
    "Human rights and civil liberties",
    "Immigration and asylum law",
    "Intellectual property",
    "Information Technology (IT) law",
    "Litigation, mediation, arbitration",
    "Personal injury, damage to goods",
    "Property law",
    "Public law",
    "Social security law",
    "Succession law",
    "Tax law",
    "Traffic and transport law"
]

# EQUIP THE RECEPTIONIST WITH A QUERY TOOL?
receptionist_prompt = f"""
You are a front-facing receptionist that handles inquiries about EU law.
You are required to do the following:

1.  Reformulate and improve queries;
2.  Identify ALL practice areas RELEVANT to the reformulated query and group the relevant sub-queries according to each area;
3.  Respond to queries accordingly.

You will be prompted to do each of these tasks, one at a time.
"""

receptionist_step_prompts = [
    """
    1.  Reformulate the user's query via decomposition and/or adding sufficient context.
        Ensure that queries/sub-queries are atomic to facilitate downstream SPARQL queries.
        Collect the resulting query/sub-queries in a list.
        Determine if the user's query is general or complex.
        If the query is general, proceed to step 3 after the outputting the JSON dictionary.

        Output the following JSON dictionary:
        {{
            "improved_query": [reformulated_query_list],
            "next_step": 2 or 3 # depending on step 1
        }}

        User query: {query}
    """,

    """
    2.  List ALL practice areas from the list below RELEVANT to the reformulated query:
        Bankruptcy and insolvency law, Commercial law, Consumer law, Criminal law, Employment law, EU law, Family law, Human rights and civil liberties, Immigration and asylum law, Intellectual property, Information Technology (IT) law, Litigation, mediation, arbitration, Personal injury, damage to goods, Property law, Public law, Social security law, Succession law, Tax law, Traffic and transport law

        Then, route each query to the most relevant, identified practice areas.
        Each query can be routed to more than one practice area.

        Output the following JSON dictionary:
        {{
            "routes": [
                {{
                    "query": "reformulated_query_1",
                    "targets": ["area_1", "area_2", "area_3", ...]
                }}
            ],
            "improved_query": [reformulated_query_list],
            "practice_areas": ["area_1", "area_2", "area_3", ...],
            "next_step": 3
        }}

        Reformulated Query: {improved_query}
    """,

    """
    3.  Respond to the reformulated query.
        If you performed step 2, inform the user that you shall forward the query all relevant experts in the identified practice areas instead.

        Output the following JSON dictionary:
        {{
            "routes": [
                {{
                    "query": "reformulated_query_1",
                    "targets": ["area_1", "area_2", "area_3", ...]
                }}
            ],
            "improved_query": [reformulated_query_list],
            "practice_areas": ["area_1", "area_2", "area_3", ...],
            "response": "your_response"
        }}

        Reformulated query: {improved_query}
    """
]

sparql_agent_prompt = """
You are a sub-agent that performs SPARQL query operations.
You are required to do the following:

1.  Choose an appropriate query template that best matches the user query;
    Extract synonyms from keywords in the provided user query.
2.  Construct a statement for each quad (source document + triple) returned from the results.

You will be prompted to do each of these tasks, one at a time.
DO NOT answer the user directly or interpret results beyond verbalization.
"""

# CURRENTLY EXCLUDES 1-HOP QUERIES
sparql_step_prompts = [
    """
    1.  DETERMINE ONE query type from the list below that matches the logic of the original query:
        ["and", "or", "not", "and_or_not", "subject_only", "predicate_only", "object_only", "subject_and_object", "subject_and_predicate", "predicate_and_object", "subject_or_object", "subject_or_predicate", "predicate_or_object"]
    
        Then, for each required component (subject, predicate, object), compile synonyms, related terms, abbreviations, broader/narrower terms, and domain jargon that could represent the same concept in the graph.

        Also include closely related sub-concepts and real-world manifestations of the concept — e.g. for "financial regulation", also consider what it governs in practice, such as lending, interest, capital, liquidity, and compliance standards.

        Prefer word stems over full phrases, and strongly prefer nested AND combos over single stems wherever possible — e.g. "fiscal policy" becomes ["fiscal", "polic"] rather than "fiscal" or "polic" alone.
        For each concept, iterate over all meaningful stem combinations — if a concept has multiple synonyms, pair each synonym stem with each other synonym stem to produce multiple AND combos rather than anchoring one stem and varying the other.
        For example, for "labor law" with synonyms "work/emploi/labour" and "law/legislat/rule", produce ["work", "law"], ["work", "legislat"], ["employ", "law"], ["employ", "legislat"], ["labour", "law"], etc. rather than just ["labour", "law"].
        Plain strings are OR-ed; nested lists are AND-ed — e.g. ["legislat", ["fiscal", "polic"], "act"] matches "legislat" OR ("fiscal" AND "polic") OR "act".
        Never include a broad or generic stem (e.g. "legislat", "act", "rule", "provis") as a plain string on its own — these must always appear inside a nested AND combo paired with a more specific stem that scopes the concept.
        Reserve single plain stems only for highly specific terms that are already precise enough to be unambiguous on their own.

        You MUST call the sparql_query tool and pass in the query type and compiled synonyms.
        Do NOT simulate, guess, or return placeholder results.

    Output the following JSON dictionary:
        {{
            "results": ["triples_returned_from_the_sparql_tool"], 
            "next_step": 2
        }}

        User query: {query}
    """,

    """
    2.  Construct a statement for each quad (source, subject, predicate, object) returned from the results in the following format:
        "Source: Statement in natural language"
    
    DO NOT MAKE ANY TOOL CALLS AFTER THIS STEP.    

    Output the following JSON dictionary:
        {{
            "results": ["triples_returned_from_the_sparql_tool"],
            "statements": ["list_of_source-labeled_statements"]
        }}

        Results: {results}

    """
    ]

legal_expert_list = []

for area in practice_areas:
    prompt = f"""
    You are a EU legal researcher in the following practice area: {area}.
    You are required to analyze the given queries/sub-queries STRICTLY WITHIN your practice area.
    You will be tasked to do the following:

    1.  For each query/sub-query, call a SPARQL sub-agent via the call_sparql_subagents tool.
    2.  Use the IRAC (Issue-Rules-Application-Conclusion) framework to analyze the results.
    3.  Organize the results into a coherent argument.

    You will be prompted to do each of these tasks, one at a time.
    """

    step_prompts = [
        """
        1. For each query/sub-query provided, call the call_sparql_subagents tool.

            SCOPE:  Only retrieve information that falls within your designated practice area.
                    Do not retrieve information outside of it, even if the query implies it.

            QUERY MODIFICATION: If a sub-query is incomplete or inadequate, apply only the 
                                minimal changes needed to make it functional. Do not restructure 
                                or expand its intent.

            QUERY CONSTRAINTS: 
                - Only append terms that narrow the query to your practice area.
                - Do not reference specific source documents, directives, statutes, or instruments.
                - Do not introduce new legal concepts beyond what the query already implies.
            

            Output the following JSON dictionary:
            {{
                "compiled_results": ["statement_1", "statement_2", ...],
                "queries_to_recall": [],   // Always empty at this step. Do not populate.
                "next_step": 2             // Always 2. Do not modify.
            }}

            Query List: {query}
        """,

        """
        2.  Evaluate the results returned by the SPARQL sub-agent(s) using the IRAC (Issue-Rules-Application-Conclusion) framework.
            If the results are satisfactory, move on to step 3;
            Otherwise, if the results are inadequate or incomprehensive,
                reformulate the corresponding query/subquery and call a SPARQL sub-agent via the sparql_agent tool.

            If there are minimal results after 2 to 3 rounds of recalling, return the results as is.
                
            Output the following JSON dictionary:
            {{
                "compiled_results": ["statement_1", "statement_2", ...],
                "queries_to_recall": ["reformulated_query_1", "reformulated_query_2", ...],
                "next_step": 2 or 3
            }}

            Compiled Results: {compiled_results}
            Query(ies) to Recall: {queries_to_recall}
        """,

        """
        3.  Organize the results into a coherent argument, as a list of propositions.
            LIST OUT ALL PROPOSITIONS, including refuting ones.

            Output the following JSON dictionary:
            {{
                "practice_area": "your practice area",
                "supporting_propositions": [list of supporting statements/propositions],
                "refuting_propositions": [list of refuting statements/propositions]
            }}

            "Compiled Results: {compiled_results}"
        """
    ]

    legal_expert_list.append({"prompt": prompt, "step_prompts": step_prompts, "practice_area": area})

evaluator_prompt = """
You are a judge with comprehensive knowledge of EU law, across all but not limited to the following practice areas:
Bankruptcy and insolvency law, Commercial law, Consumer law, Criminal law, Employment law, EU law, Family law, Human rights and civil liberties, Immigration and asylum law, Intellectual property, Information Technology (IT) law, Litigation, mediation, arbitration, Personal injury, damage to goods, Property law, Public law, Social security law, Succession law, Tax law, Traffic and transport law

You are required to do the following:
1.  Generate a COMPREHENSIVE EVALUATION on the compiled analyses through the IRAC (Issue-Rules-Application-Conclusion) framework.
2.  Compile supporting and refuting statements/propositions.
2.  Spot inconsistencies or conflicting rules and highlight them.
3.  Provide recommendations/strategies based on your analysis, and predict the most likely outcome(s), if applicable.

Output Format:
{{
    "evaluation": "a comprehensive evaluation",
    "supporting_props": [list of supporting statements/propositions],
    "refuting_props": [list of refuting statements/propositions],
    "inconsistencies": [list of conflicting/inconsistent rules],
    "recs_and strats": [list of recommendations and strategies],
    "likely_outcomes": [most likely outcomes, if applicable]
}}

Compiled Analyses: {query}
"""

from concurrent.futures import ThreadPoolExecutor

import re

def sparql_query(
    synonyms: dict[str, list[str]],
    query_type: str,
    api_key=None
    ) -> list[tuple[str, str, str, str]]:
    """
    Builds a parameterized SPARQL query from a synonym dictionary and returns the query results as a list of (subject, predicate, object, source) quads.

    Parameters
    ----------
    synonyms : dict
        Keys: "subject", "predicate", "object" — each maps to a list of synonyms.
        Example:
            {
                "subject":   ["person", "individual"],
                "predicate": ["knows", "friendOf"],
                "object":    ["city", "town"],
            }

    query_type : str
        One of:
            Logical  : "and" | "or" | "not" | "and_or_not"
            Partial  : "subject_only" | "predicate_only" | "object_only"
                       | "subject_and_object" | "subject_and_predicate" | "predicate_and_object"
                       | "subject_or_object"  | "subject_or_predicate"  | "predicate_or_object"
            One-hop  : "1hop_fixed" | "1hop_variable" | "1hop_optional"
            
    Returns
    -------
    list[tuple[str, str, str, str]]
        Each tuple is (source, subject, predicate, object).
    """

    # ------------------------------------------------------------------
    # 1. Validate inputs
    # ------------------------------------------------------------------
    print(f"[SPARQL] Called with query_type='{query_type}' | "
          f"synonym keys={list(synonyms.keys())} | "
          f"synonym counts={ {k: len(v) for k, v in synonyms.items()} }")

    REQUIRED_KEYS_BY_TYPE = {
        "and":                    {"subject", "predicate", "object"},
        "or":                     {"subject", "predicate", "object"},
        "not":                    {"subject", "predicate", "object"},
        "and_or_not":             {"subject", "predicate", "object"},
        "subject_only":           {"subject"},
        "predicate_only":         {"predicate"},
        "object_only":            {"object"},
        "subject_and_object":     {"subject", "object"},
        "subject_and_predicate":  {"subject", "predicate"},
        "predicate_and_object":   {"predicate", "object"},
        "subject_or_object":      {"subject", "object"},
        "subject_or_predicate":   {"subject", "predicate"},
        "predicate_or_object":    {"predicate", "object"},
        "1hop_fixed":             {"subject", "predicate", "object"},
        "1hop_variable":          {"subject", "predicate", "object"},
        "1hop_optional":          {"subject", "predicate", "object"},
    }

    qt = query_type.strip().lower()

    if qt not in REQUIRED_KEYS_BY_TYPE:
        print(f"[SPARQL] ✗ Unknown query_type='{qt}'")
        raise ValueError(f"Unknown query_type '{query_type}'. Valid: {sorted(REQUIRED_KEYS_BY_TYPE)}")

    required_keys = REQUIRED_KEYS_BY_TYPE[qt]
    print(f"[SPARQL] Required synonym keys for '{qt}': {required_keys}")

    missing = required_keys - synonyms.keys()
    if missing:
        print(f"[SPARQL] ✗ Missing synonym keys: {missing}")
        raise ValueError(f"query_type='{qt}' requires synonym keys: {missing}")

    for key in required_keys:
        val = synonyms[key]
        if not isinstance(val, list) or not val:
            raise ValueError(f"synonyms['{key}'] must be a non-empty list (required by query_type='{qt}')")
        for i, entry in enumerate(val):
            if isinstance(entry, list):
                if not entry or not all(isinstance(s, str) and s.strip() for s in entry):
                    raise ValueError(
                        f"synonyms['{key}'][{i}] is a multi-stem list but contains empty or non-string stems: {entry}"
                    )
            elif not isinstance(entry, str) or not entry.strip():
                raise ValueError(
                    f"synonyms['{key}'][{i}] must be a non-empty string or list of strings, got: {repr(entry)}"
                )

    print(f"[SPARQL] ✓ Validation passed")

    # ------------------------------------------------------------------
    # 2. Helper: build a CONTAINS+LCASE filter for a list of synonyms
    # ------------------------------------------------------------------
    def contains_filter(var: str, terms: list[str | list[str]]) -> str:
        clauses = []
        for t in terms:
            if isinstance(t, list):
                # Multi-stem phrase: all stems must match (AND)
                and_parts = [f'CONTAINS(LCASE(str(?{var})), "{stem.lower()}")' for stem in t]
                clauses.append("(" + " && ".join(and_parts) + ")")
            else:
                # Single stem: simple CONTAINS
                clauses.append(f'CONTAINS(LCASE(str(?{var})), "{t.lower()}")')
        return "(" + " || ".join(clauses) + ")"

    s_f = contains_filter("subject",   synonyms["subject"])   if "subject"   in required_keys else None
    p_f = contains_filter("predicate", synonyms["predicate"]) if "predicate" in required_keys else None
    o_f = contains_filter("object",    synonyms["object"])    if "object"    in required_keys else None

    print(f"[SPARQL] Filters built | s_f={'yes' if s_f else 'skipped'} "
          f"p_f={'yes' if p_f else 'skipped'} o_f={'yes' if o_f else 'skipped'}")

    # ------------------------------------------------------------------
    # 3. Build the SPARQL query string
    # ------------------------------------------------------------------
    if qt == "and":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f})
                FILTER({p_f})
                FILTER({o_f})  
            }}    
        }}
        """

    elif qt == "or":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f} || {p_f} || {o_f})
            }}
        }}
        """

    elif qt == "not":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f})
                FILTER({p_f})
                FILTER(!{o_f})
            }}
        }}
        """

    elif qt == "and_or_not":
        mid = max(1, len(synonyms["object"]) // 2)
        obj_a = contains_filter("object", synonyms["object"][:mid])
        obj_b = contains_filter("object", synonyms["object"][mid:] or synonyms["object"])
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER(
                    {s_f}
                    && ({obj_a} || {obj_b})
                    && !{p_f}
                )
            }}
        }}
        """

    elif qt == "subject_only":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f})
            }}
        }}"""

    elif qt == "predicate_only":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({p_f})
            }}
        }}
        """

    elif qt == "object_only":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({o_f})
            }}
        }}
        """

    elif qt == "subject_and_object":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f})
                FILTER({o_f})
            }}
        }}
        """

    elif qt == "subject_and_predicate":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f})
                FILTER({p_f})
            }}
        }}
        """

    elif qt == "predicate_and_object":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({p_f})
                FILTER({o_f})
            }}
        }}
        """

    elif qt == "subject_or_object":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f} || {o_f})
            }}
        }}
        """

    elif qt == "subject_or_predicate":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f} || {p_f})
            }}
        }}
        """

    elif qt == "predicate_or_object":
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({p_f} || {o_f})
            }}
        }}
        """

    elif qt == "1hop_fixed":
        pred_values = " ".join(f"<urn:placeholder:{p}>" for p in synonyms["predicate"])
        s_f2 = contains_filter("subject", synonyms["subject"])
        o_f2 = contains_filter("object",  synonyms["object"])
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                VALUES ?predicate {{ {pred_values} }}
                FILTER({s_f2})
                FILTER({o_f2})
            }}
        }}
        """

    elif qt == "1hop_variable":
        s_f2 = contains_filter("subject",   synonyms["subject"])
        p_f2 = contains_filter("predicate", synonyms["predicate"])
        o_f2 = contains_filter("object",    synonyms["object"])
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                FILTER({s_f2} && {p_f2} && {o_f2})
            }}
        }}
        """

    elif qt == "1hop_optional":
        pred_values = " ".join(f"<urn:placeholder:{p}>" for p in synonyms["predicate"])
        s_f2 = contains_filter("subject", synonyms["subject"])
        o_f2 = contains_filter("object",  synonyms["object"])
        query = f"""
        SELECT ?graph ?subject ?predicate ?object WHERE {{
            GRAPH ?graph {{
                ?subject ?predicate ?object .
                VALUES ?predicate {{ {pred_values} }}
                FILTER({s_f2})
                OPTIONAL {{
                    FILTER({o_f2})
                }}
            }}
        }}
        """

    print(f"[SPARQL] Query built for '{qt}' ({len(query)} chars)")
    print(f"[SPARQL] Query:\n{query}")

    # ------------------------------------------------------------------
    # 4. Execute and parse results into (source, subject, predicate, object) quads
    # ------------------------------------------------------------------
    def shorten(uri):
        uri = str(uri)
        return uri.split("/")[-1].split("#")[-1]

    print(f"[SPARQL] Executing query against eu_graph...")
    t0 = time.perf_counter()

    try:
        results = eu_graph.query(query)
    except Exception as e:
        print(f"[SPARQL] ✗ Query execution failed: {type(e).__name__}: {e}")
        raise

    elapsed = time.perf_counter() - t0
    row_vars = [str(v) for v in results.vars]
    print(f"[SPARQL] ✓ Query executed in {elapsed:.3f}s | "
          f"result vars={row_vars}")

    quads: list[tuple[str, str, str, str]] = []

    for i, row in enumerate(results):
        if "subject" in row_vars:
            source = shorten(row.graph) if "graph" in row_vars and row.graph else ""
            quad = (source, shorten(row.subject), shorten(row.predicate), shorten(row.object))
            quads.append(quad)

            if i < 3:
                print(f"[SPARQL] Row {i}: source='{source}' | "
                      f"s='{shorten(row.subject)[:60]}' | "
                      f"p='{shorten(row.predicate)[:60]}' | "
                      f"o='{shorten(row.object)[:60]}'")

        elif "entity" in row_vars:
            if row.hop1Pred:
                quad = ("", shorten(row.entity), shorten(row.hop1Pred), shorten(row.intermediate))
                quads.append(quad)
                if i < 3:
                    print(f"[SPARQL] Row {i} hop1: "
                          f"'{shorten(row.entity)[:60]}' -> "
                          f"'{shorten(row.hop1Pred)[:60]}' -> "
                          f"'{shorten(row.intermediate)[:60]}'")

            if getattr(row, "hop2Pred", None) and getattr(row, "target", None):
                quad = ("", shorten(row.intermediate), shorten(row.hop2Pred), shorten(row.target))
                quads.append(quad)
                if i < 3:
                    print(f"[SPARQL] Row {i} hop2: "
                          f"'{shorten(row.intermediate)[:60]}' -> "
                          f"'{shorten(row.hop2Pred)[:60]}' -> "
                          f"'{shorten(row.target)[:60]}'")

    print(f"[SPARQL] ✓ Parsed {len(quads)} quads total")
    return quads

sparql_tool_dict = {
    sparql_query: {
        "type": "function",
        "function": {
            "name": "sparql_query_builder",
            "description": """
                Builds and executes a parameterized SPARQL query on an RDF graph.
                Selects the appropriate query type, then extracts keywords and synonyms from the user query, and assigns them to subject, predicate, and object slots.
                Returns results as a list of (source, subject, predicate, object) quads.
                """,
            "parameters": {
                "type": "object",
                "properties": {
                    "synonyms": {
                        "type": "object",
                        "description": (
                            "A dict of three lists of synonyms, one per triple component. "
                            "For 2-hop query types, the predicate list is order-sensitive: "
                            "the first half is assigned to hop 1, the second half to hop 2."
                        ),
                        "properties": {
                            "subject": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}}
                                    ]
                                },
                                "description": (
                                    "Synonyms for the subject slot. Each entry is either a single stem (string) "
                                    "or a list of stems that must ALL appear (AND logic). "
                                    "Multiple entries are OR-ed together. "
                                    "Example: ['regulat', ['climat', 'polic']] matches 'regulat' OR ('climat' AND 'polic')."
                                )
                            },
                            "predicate": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}}
                                    ]
                                },
                                "description": (
                                    "Synonyms for the predicate slot. Each entry is either a single stem (string) "
                                    "or a list of stems that must ALL appear (AND logic). "
                                    "Multiple entries are OR-ed together."
                                )
                            },
                            "object": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}}
                                    ]
                                },
                                "description": (
                                    "Synonyms for the object slot. Each entry is either a single stem (string) "
                                    "or a list of stems that must ALL appear (AND logic). "
                                    "Multiple entries are OR-ed together."
                                )
                            }
                        },
                        "required": ["subject", "predicate", "object"]
                    },
                    "query_type": {
                        "type": "string",
                        "description": "The SPARQL query template to use.",
                        "enum": [
                            "and", "or", "not", "and_or_not",
                            "subject_only", "predicate_only", "object_only",
                            "subject_and_object", "subject_and_predicate", "predicate_and_object",
                            "subject_or_object", "subject_or_predicate", "predicate_or_object",
                            "1hop_fixed", "1hop_variable", "1hop_optional"
                        ]
                    }
                },
                "required": ["synonyms", "query_type"]
            }
        }
    }
}
def call_sparql_subagents(queries, api_key):
    """Receives a list of queries, and instantiates sparql sub-agents to handle each query using SPARQL."""
    results = list()
    local_key = api_key
    
    def sub_agent_thread(query):
        sub_agent = Legal_Agent(
                system_prompt=sparql_agent_prompt,
                step_prompts=sparql_step_prompts,
                api_key=local_key,
                tool_table=sparql_tool_dict
            )
        return sub_agent.sequential_reasoning(query)

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(sub_agent_thread, queries))

    return results

sparql_batch_tool_dict = {
    call_sparql_subagents: {
        "type": "function",
        "function": {
            "name": "call_sparql_subagents",
            "description": "Receives a list of queries, and instantiates sparql sub-agents to handle each query using SPARQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {
                            "type": "string"
                            },
                        "description": "A list of natural language queries to be converted into SPARQL."
                    }
                },
                "required": ["queries"]
            }
        }
    }
}

# Agents
receptionist = Legal_Agent(
    system_prompt=receptionist_prompt,
    step_prompts=receptionist_step_prompts,
    api_key=RECEPTIONIST_KEY
    )

legal_expert_lookup = {}
for expert in legal_expert_list:
    expert_instance = Legal_Agent(
        system_prompt=expert["prompt"],
        step_prompts=expert["step_prompts"],
        tool_table=sparql_batch_tool_dict,
        api_key=EXPERT_KEYS[expert["practice_area"]]
    )
    legal_expert_lookup[expert["practice_area"]] = expert_instance

test_expert = legal_expert_lookup["EU law"]

sparql_agent = Legal_Agent(
    system_prompt=sparql_agent_prompt,
    step_prompts=sparql_step_prompts,
    api_key=openai.api_key,
    tool_table=sparql_tool_dict
    )


evaluator = Legal_Agent(
    system_prompt=evaluator_prompt,
    api_key=EVALUATOR_KEY
    )

def receptionist_seq_reasoning(query):
    receptionist.sequential_reasoning(query)



def analyze_query(query):
    # Screening by the Receptionist Agent
    screened_results = receptionist.sequential_reasoning(query)

    print("Finished screening query")

    receptionist_response = screened_results.get("response")
    routed_queries = screened_results.get("routes")  # List of {query, targets}
    relev_areas = screened_results.get("practice_areas")

    print("Finished parsing receptionist's response")

    if not relev_areas:
        print("Proceeding to general response")
        return receptionist_response

    else:
        print("Calling experts:")

        # --- Invert routes: map each area -> list of queries targeting it ---
        area_to_queries: dict[str, list[str]] = {area: [] for area in relev_areas}

        for route in routed_queries:
            query = route["query"]
            for target in route["targets"]:
                if target in area_to_queries:
                    area_to_queries[target].append(query)

        # --- Build expert lookup (unchanged) ---
        legal_expert_lookup = {}
        for expert in legal_expert_list:
            if expert["practice_area"] in relev_areas:
                expert_instance = Legal_Agent(
                    system_prompt=expert["prompt"],
                    step_prompts=expert["step_prompts"],
                    tool_table=sparql_batch_tool_dict,
                    api_key=EXPERT_KEYS[expert["practice_area"]]
                )
                legal_expert_lookup[expert["practice_area"]] = expert_instance

        # --- Pair each expert with its corresponding queries ---
        expert_query_pairs = [
            (legal_expert_lookup[area], area_to_queries[area])
            for area in relev_areas
            if area in legal_expert_lookup and area_to_queries[area]  # skip if no queries routed
        ]

        def expert_thread(pair):
            expert_agent, queries = pair
            print(expert_agent.context[-1])
            return expert_agent.sequential_reasoning(queries)  # passes only relevant queries

        print("Starting batch calls:")

        with ThreadPoolExecutor() as executor:
            expert_analyses = list(executor.map(expert_thread, expert_query_pairs))

        # Output format of a Legal Expert Agent
        #   {
        #       "practice_area": {area},
        #       "supporting_propositions": [list of supporting statements/propositions],
        #       "refuting_propositions": [list of refuting statements/propositions]
        #   }

        formatted_analyses = list()
        for analysis in expert_analyses:
            area = analysis.get("practice_area")
            support_props = analysis.get("supporting_propositions")
            refute_props = analysis.get("refuting_propositions")

            support_props_indexed = [f"{idx + 1}.\t{prop}" for idx, prop in enumerate(support_props)]
            refute_props_indexed = [f"{idx + 1}.\t{prop}" for idx, prop in enumerate(refute_props)]

            support_props_concat = "\n".join(support_props_indexed)
            refute_props_concat = "\n".join(refute_props_indexed)

            pretty_analysis = f"""
            Practice Area:\t{area}

            Supporting Propositions:
            {support_props_concat}

            Refuting Propositions:
            {refute_props_concat}
            -------------------------
            """

            formatted_analyses.append(pretty_analysis)

        concatenated_analyses = "\n".join(formatted_analyses)

        print("Passing analyses to evaluator:")

        final_result = json.loads(evaluator.respond_to(concatenated_analyses))

        # Output format of the Evaluator Agent
        #   {
        #       "evaluation": "a comprehensive evaluation",
        #       "supporting_props": [list of supporting statements/propositions],
        #       "refuting_props": [list of refuting statements/propositions],
        #       "inconsistencies": [list of conflicting/inconsistent rules],
        #       "recs_and strats": [list of recommendations and strategies],
        #       "likely_outcomes": [most likely outcomes, if applicable]
        #   }
        
        final_eval = final_result.get("evaluation")
        supporting_props = final_result.get("supporting_props")
        refuting_props = final_result.get("refuting_props")
        inconsistencies = final_result.get("inconsistencies")
        recs_and_strats = final_result.get("recs_and_strats")
        likely_outcomes = final_result.get("likely_outcomes")

        supporting_props_indexed = [f"{idx + 1}.\t{prop}" for idx, prop in enumerate(supporting_props)]
        refuting_props_indexed = [f"{idx + 1}.\t{prop}" for idx, prop in enumerate(refuting_props)]
        inconsistencies_indexed = [f"{idx + 1}.\t{inconsistency}" for idx, inconsistency in enumerate(inconsistencies)]
        recs_and_strats_indexed = [f"{idx + 1}.\t{rec}" for idx, rec in enumerate(recs_and_strats)]
        likely_outcomes_indexed = [f"{idx + 1}.\t{outcome}" for idx, outcome in enumerate(likely_outcomes)]

        supporting_props_concat = "\n".join(supporting_props_indexed)
        refuting_props_concat = "\n".join(refuting_props_indexed)
        inconsistencies_concat = "\n".join(inconsistencies_indexed)
        recs_and_strats_concat = "\n".join(recs_and_strats_indexed)
        likely_outcomes_concat = "\n".join(likely_outcomes_indexed)

        final_response = f"""
        Evaluation:
        {final_eval}

        Supporting Propositions:
        {supporting_props_concat}

        Refuting Propositions:
        {refuting_props_concat}

        Inconsistencies/Conflicting Rules:
        {inconsistencies_concat}

        Recommendations and Strategies:
        {recs_and_strats_concat}
        """

        if likely_outcomes_concat:
            final_response += "\n"
            final_response += f"""
            Likely Outcomes:
            {likely_outcomes_concat}
            """

        return final_response