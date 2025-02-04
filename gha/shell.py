from typing import Literal, Optional, Union

from gha.step import StepBase

ShellKind = Union[
    Literal["bash"],
    Literal["pwsh"],
    Literal["python"],
    Literal["sh"],
    Literal["cmd"],
    Literal["powershell"],
]
"""Type of the shell to use."""


class ShellAction(StepBase):
    """Runs command-line programs in system shell."""

    run: str
    """The command to run."""

    shell: Optional[ShellKind] = None
    """The shell to use for running the command."""

    working_directory: Optional[str] = None
    """The working directory for the step."""
