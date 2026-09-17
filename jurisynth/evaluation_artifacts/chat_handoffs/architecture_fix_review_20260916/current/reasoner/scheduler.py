"""Dependency-aware leaf scheduler; it owns concurrency, not Retrieval Mech."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from jurisynth.agentic_reasoner.models import LeafNode, NodeResult, NodeStatus


LeafExecutor = Callable[[LeafNode, list], Awaitable[object]]


async def execute_dependency_plan(
    nodes: list[LeafNode], executor: LeafExecutor, *, max_concurrency: int = 4
) -> dict[str, NodeResult]:
    """Run ready leaves concurrently and block only dependants of failed leaves."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    node_by_id = {node.query_id: node for node in nodes}
    if len(node_by_id) != len(nodes):
        raise ValueError("query_ids must be unique")
    unknown = {
        dependency for node in nodes for dependency in (*node.dependency_ids, *node.optional_dependency_ids)
        if dependency not in node_by_id
    }
    if unknown:
        raise ValueError(f"Unknown dependency IDs: {sorted(unknown)}")

    results = {node.query_id: NodeResult(NodeStatus.WAITING) for node in nodes}
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run(node: LeafNode):
        async with semaphore:
            dependency_answers = [
                results[key].answer for key in (*node.dependency_ids, *node.optional_dependency_ids)
                if results[key].status == NodeStatus.COMPLETE and results[key].answer is not None
            ]
            results[node.query_id].status = NodeStatus.RUNNING
            try:
                answer = await executor(node, dependency_answers)
            except Exception as exc:  # keep unrelated branches running
                results[node.query_id] = NodeResult(NodeStatus.FAILED, error=repr(exc))
            else:
                results[node.query_id] = NodeResult(NodeStatus.COMPLETE, answer=answer)

    running: dict[str, asyncio.Task[None]] = {}
    while True:
        for node in nodes:
            if results[node.query_id].status != NodeStatus.WAITING:
                continue
            dependencies = [results[key].status for key in node.dependency_ids]
            if any(state in {NodeStatus.FAILED, NodeStatus.BLOCKED} for state in dependencies):
                results[node.query_id] = NodeResult(
                    NodeStatus.BLOCKED,
                    error="required dependency did not complete",
                )
            elif all(state == NodeStatus.COMPLETE for state in dependencies):
                results[node.query_id].status = NodeStatus.READY
                running[node.query_id] = asyncio.create_task(run(node))

        if not running:
            unresolved = [
                node.query_id
                for node in nodes
                if results[node.query_id].status == NodeStatus.WAITING
            ]
            if unresolved:
                raise ValueError(f"Dependency cycle detected: {unresolved}")
            return results

        done, _ = await asyncio.wait(
            tuple(running.values()),
            return_when=asyncio.FIRST_COMPLETED,
        )
        await asyncio.gather(*done)
        completed_ids = {
            query_id
            for query_id, task in running.items()
            if task in done
        }
        for query_id in completed_ids:
            del running[query_id]
