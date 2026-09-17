import pytest

from jurisynth.agentic_reasoner.qcompiler_adapter import QCompilerAdapter, parse_and_adapt


class Node:
    def __init__(self, node_type, value=None, children=None, placeholder=None):
        self.type = node_type
        self.value = value
        self.children = children
        self.placeholder = placeholder


def test_list_branches_are_independent_and_dependent_right_branch_waits_for_left():
    tree = Node(
        "ListQuery",
        children=[
            Node("AtomicQuery", "independent question"),
            Node(
                "DependentQuery",
                children=[
                    Node("AtomicQuery", "find the directive"),
                    Node("AtomicQuery", "what does {directive} require?", placeholder=["directive"]),
                ],
            ),
        ],
    )

    leaves = QCompilerAdapter().adapt(tree, contextual_facts=("EU law",))

    assert [(leaf.query_id, leaf.dependency_ids) for leaf in leaves] == [
        ("q001", ()),
        ("q002", ()),
        ("q003", ("q002",)),
    ]
    assert leaves[2].constraints == {"qcompiler_placeholders": ("directive",)}
    assert all(leaf.contextual_facts == ("EU law",) for leaf in leaves)


def test_adapter_rejects_malformed_or_unknown_nodes():
    with pytest.raises(ValueError, match="non-empty"):
        QCompilerAdapter().adapt(Node("AtomicQuery", " "))
    with pytest.raises(ValueError, match="exactly two"):
        QCompilerAdapter().adapt(Node("DependentQuery", children=[Node("AtomicQuery", "one")]))
    with pytest.raises(ValueError, match="Unsupported"):
        QCompilerAdapter().adapt(Node("Unknown"))


def test_pinned_compatible_parser_builds_a_real_dependency_plan():
    leaves = parse_and_adapt(
        "find the Directive * what does {Directive} require + independent question",
        contextual_facts=("EU law",),
    )
    assert [(leaf.query, leaf.dependency_ids) for leaf in leaves] == [
        ("find the Directive", ()),
        ("what does {Directive} require", ("q001",)),
        ("independent question", ()),
    ]
