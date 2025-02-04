from typing import Dict, Optional

from pydantic import Field

from gha.core import GhaModel


class StepBase(GhaModel):
    """Configures a step in GitHub Actions workflow."""

    id: Optional[str] = None
    """A unique identifier for the step."""

    name: Optional[str] = None
    """A descriptive name for the step."""

    env: Optional[Dict[str, str]] = None
    """A map of environment variables to set for the step."""

    continue_on_error: Optional[bool] = None
    """Whether to continue running the job if the step fails."""

    timeout_minutes: Optional[int] = None
    """The maximum time to run the step before it is automatically cancelled."""

    exec_if: Optional[str] = Field(alias="if", default=None)
    """A conditional expression that determines whether the step runs."""
