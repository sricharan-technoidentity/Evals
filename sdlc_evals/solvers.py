"""Solvers: prepare the sandbox repo, then run the agent under test."""

from __future__ import annotations

from inspect_ai.agent import AgentPrompt, AgentSubmit, react
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import sandbox, store

from .tools import REPO_DIR, agent_tools

BASE_SHA_KEY = "base_sha"

# --- prompt variants ------------------------------------------------------------------
# Add a new key here and run with `-T prompt_variant=<key>` to compare prompt versions.

_COMMON = """You are a software engineer working on a ticket in a git repository.
The repository is already cloned and dependencies are installed. Your working directory
is the repository root. Use the tools to explore the code, make the change, and run the
project's tests and checks.

Rules:
- Work only inside the repository. Do not push, do not create real pull requests, do not
  change git remotes, do not publish anything.
- Do not weaken the project's quality gates (coverage thresholds, lint/format config,
  build files) and do not delete existing tests.

When you are done, call `submit_pr` with a pull-request description in Markdown:
a title line, a short summary of what changed and why, the files touched, and exactly
which commands you ran to test it and their results. Only claim what you actually did."""

PROMPTS: dict[str, str] = {
    "v1": _COMMON,
    "v2": _COMMON
    + """

Working style:
- Before editing, find the existing tests for the code you will change and read them.
- Keep the diff minimal: change only what the ticket needs. No drive-by refactors.
- Add or update tests that prove each acceptance criterion.
- Before submitting, run the full test, lint, type-check and format commands the project
  uses (look in package.json / pom.xml) and fix anything that fails. If the project has a
  formatter (e.g. `pnpm exec biome format --write`, `./mvnw spring-javaformat:apply`), run it.""",
}


@solver
def checkout_repo() -> Solver:
    """Clone the ticket's repo at its pinned commit into the sandbox and run setup."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        repo = state.metadata["repo"]
        sbx = sandbox()

        async def run(cmd: str, cwd: str | None = REPO_DIR, timeout: int = 1800) -> None:
            r = await sbx.exec(["bash", "-c", cmd], cwd=cwd, timeout=timeout)
            if not r.success:
                raise RuntimeError(f"Setup command failed: {cmd}\n{r.stderr[-3000:]}\n{r.stdout[-3000:]}")

        await run(f"git clone --quiet {repo['url']} {REPO_DIR}", cwd=None)
        await run(f"git checkout --quiet {repo['commit']}")
        await run("git config user.email agent@example.invalid && git config user.name 'Eval Agent'")
        # no remote = nothing to push to, whatever the agent tries (defence in depth)
        await run("git remote remove origin")
        for cmd in state.metadata.get("setup", []):
            await run(cmd)

        r = await sbx.exec(["git", "rev-parse", "HEAD"], cwd=REPO_DIR)
        store().set(BASE_SHA_KEY, r.stdout.strip())
        return state

    return solve


def ticket_agent(prompt_variant: str = "v1"):
    if prompt_variant not in PROMPTS:
        raise ValueError(f"Unknown prompt_variant {prompt_variant!r}; choose from {sorted(PROMPTS)}")
    return react(
        name="ticket_agent",
        description="Implements a ticket in a repository and proposes a PR description.",
        prompt=AgentPrompt(instructions=PROMPTS[prompt_variant]),
        tools=agent_tools(),
        submit=AgentSubmit(
            name="submit_pr",
            description="Submit your pull-request description (Markdown) once the change is complete.",
            answer_only=True,
        ),
    )
