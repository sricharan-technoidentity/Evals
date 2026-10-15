"""Inspect task: ticket -> PR.

Kiro CLI as the agent under test (uses KIRO_API_KEY):
    inspect eval ticket_to_pr.py -T agent=kiro --model kiro/claude-sonnet-4.6 \
        --model-role grader=kiro/claude-sonnet-4.6

Inspect's own react agent over a model API (e.g. Anthropic):
    inspect eval ticket_to_pr.py -T agent=react --model anthropic/claude-sonnet-5-5 \
        --model-role grader=anthropic/claude-haiku-5-5
"""

from __future__ import annotations

import os
from pathlib import Path

from inspect_ai import Task, task

from sdlc_evals.dataset import ticket_dataset
from sdlc_evals.kiro import kiro_cli_agent
from sdlc_evals.scorers import acceptance_tests, checks_pass, diff_scope, pr_description, pr_ready, safe_actions
from sdlc_evals.solvers import checkout_repo, ticket_agent

COMPOSE_FILE = Path(__file__).resolve().parent / "docker" / "compose.yaml"


@task
def ticket_to_pr(
    tickets: str | None = None,
    agent: str | None = None,
    prompt_variant: str = "v1",
    kiro_model: str | None = None,
    kiro_sandbox: bool = False,
    sandbox: str = "local",
    message_limit: int = 80,
    working_limit: int = 1800,
) -> Task:
    """Evaluate an agent that turns a ticket into a proposed PR.

    Args:
      tickets: Comma-separated ticket ids or fixture names (default: all).
      agent: "kiro" (Kiro CLI headless) or "react" (Inspect's agent over a model API).
        Defaults to $SDLC_AGENT, else "kiro".
      prompt_variant: System-prompt version for the react agent (see solvers.PROMPTS).
      kiro_model: Kiro model id for the agent. Defaults to the id in --model when
        --model is kiro/<id>, else Kiro's own default.
      kiro_sandbox: Pass --sandbox to kiro-cli (Kiro's local command sandbox).
      sandbox: Inspect sandbox: "local" (no isolation) or "docker".
      message_limit: Max messages (react agent only).
      working_limit: Max seconds of agent working time per sample.
    """
    agent = agent or os.environ.get("SDLC_AGENT", "kiro")
    if agent == "kiro":
        solver_agent = kiro_cli_agent(model=kiro_model, kiro_sandbox=kiro_sandbox, timeout=working_limit)
    elif agent == "react":
        solver_agent = ticket_agent(prompt_variant)
    else:
        raise ValueError(f"agent must be 'kiro' or 'react', got {agent!r}")

    sandbox_spec = ("docker", str(COMPOSE_FILE)) if sandbox == "docker" else "local"
    return Task(
        dataset=ticket_dataset(tickets),
        solver=[checkout_repo(), solver_agent],
        scorer=[diff_scope(), checks_pass(), acceptance_tests(), safe_actions(), pr_description(), pr_ready()],
        sandbox=sandbox_spec,
        message_limit=message_limit,
        working_limit=working_limit + 600,  # headroom for setup on top of the agent's own timeout
        metadata={"agent": agent, "kiro_model": kiro_model, "prompt_variant": prompt_variant, "sandbox": sandbox},
        version=2,
    )
