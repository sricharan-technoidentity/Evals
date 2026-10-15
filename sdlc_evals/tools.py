"""Tools given to the agent under test.

They all go through `sandbox()`, so they work unchanged with Inspect's `local` sandbox
or a `docker` sandbox. Every command runs with the cloned repository as working dir.
"""

from __future__ import annotations

from inspect_ai.tool import Tool, ToolError, tool
from inspect_ai.util import sandbox, store

from .policy import check_command, check_path

REPO_DIR = "repo"
BLOCKED_KEY = "blocked_actions"


def _record_block(kind: str, detail: str, reason: str) -> None:
    blocked = store().get(BLOCKED_KEY, [])
    blocked.append({"kind": kind, "detail": detail[:500], "reason": reason})
    store().set(BLOCKED_KEY, blocked)


@tool
def bash(timeout: int = 900) -> Tool:
    """Bash in the repository, with a deny-list for destructive or out-of-scope actions."""

    async def execute(command: str) -> str:
        """Run a bash command from the repository root.

        Args:
          command: The bash command to execute.

        Returns:
          Combined stderr and stdout of the command, plus its exit code.
        """
        rule = check_command(command)
        if rule is not None:
            _record_block("bash", command, rule.reason)
            return f"BLOCKED by policy ({rule.name}): {rule.reason} The command was not run."

        result = await sandbox().exec(["bash", "-c", command], cwd=REPO_DIR, timeout=timeout)
        out = ""
        if result.stderr:
            out += result.stderr if result.stderr.endswith("\n") else result.stderr + "\n"
        out += result.stdout
        return f"{out}\n[exit code: {result.returncode}]"

    return execute


@tool
def view_file() -> Tool:
    async def execute(path: str, start_line: int = 1, end_line: int = -1) -> str:
        """View a file in the repository with line numbers.

        Args:
          path: File path relative to the repository root.
          start_line: First line to show (1-based).
          end_line: Last line to show, or -1 for end of file.

        Returns:
          The requested lines, each prefixed with its line number.
        """
        if reason := check_path(path):
            _record_block("view_file", path, reason)
            raise ToolError(reason)
        try:
            text = await sandbox().read_file(f"{REPO_DIR}/{path}")
        except FileNotFoundError:
            raise ToolError(f"File not found: {path}")
        lines = text.splitlines()
        end = len(lines) if end_line == -1 else min(end_line, len(lines))
        start = max(start_line, 1)
        return "\n".join(f"{i:>5}\t{lines[i - 1]}" for i in range(start, end + 1))

    return execute


@tool
def write_file() -> Tool:
    async def execute(path: str, content: str) -> str:
        """Create or overwrite a file in the repository.

        Args:
          path: File path relative to the repository root.
          content: Full new content of the file.

        Returns:
          Confirmation message.
        """
        if reason := check_path(path):
            _record_block("write_file", path, reason)
            raise ToolError(reason)
        await sandbox().write_file(f"{REPO_DIR}/{path}", content)
        return f"Wrote {len(content)} characters to {path}"

    return execute


@tool
def replace_in_file() -> Tool:
    async def execute(path: str, old: str, new: str) -> str:
        """Replace exactly one occurrence of `old` with `new` in a repository file.

        Args:
          path: File path relative to the repository root.
          old: Exact text to replace. Must occur exactly once in the file.
          new: Replacement text.

        Returns:
          Confirmation message.
        """
        if reason := check_path(path):
            _record_block("replace_in_file", path, reason)
            raise ToolError(reason)
        try:
            text = await sandbox().read_file(f"{REPO_DIR}/{path}")
        except FileNotFoundError:
            raise ToolError(f"File not found: {path}")
        count = text.count(old)
        if count != 1:
            raise ToolError(f"`old` must occur exactly once in {path}; found {count} occurrences.")
        await sandbox().write_file(f"{REPO_DIR}/{path}", text.replace(old, new, 1))
        return f"Replaced 1 occurrence in {path}"

    return execute


def agent_tools() -> list[Tool]:
    return [bash(), view_file(), write_file(), replace_in_file()]
