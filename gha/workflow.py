from typing import Dict, Optional

import yaml

from gha.core import GhaModel
from gha.event import PushEventTrigger
from gha.job import Concurrency, DefaultStepSettings, Job
from gha.permission import Permission, Permissions


class _NoSingleQuotesDumper(yaml.SafeDumper):
    def represent_scalar(self, tag, value, style=None):
        if style is None and value == "on":
            style = ""
        return super().represent_scalar(tag, value, style)


class _Events(GhaModel):
    """Configures automatic triggers that will cause workflow to run."""

    push: Optional[PushEventTrigger] = None
    """Runs the workflow when a commit or tag is pushed, or when a repository is created from a template."""


class _Workflow(GhaModel):
    """A workflow is a configurable automated process made up of one or more jobs."""

    name: Optional[str] = None
    """The name of the workflow."""

    run_name: Optional[str] = None
    """The name for workflow runs generated from the workflow."""

    on: Optional[_Events] = None
    """To automatically trigger a workflow, use on to define which events can cause the workflow to run."""

    permissions: Optional[Permissions] = None
    """You can use permissions to modify the default permissions granted to the GITHUB_TOKEN, adding or removing access as required, so that you only allow the minimum required access."""

    env: Optional[Dict[str, str]] = None
    """A map of variables that are available to the steps of all jobs in the workflow."""

    defaults: Optional[DefaultStepSettings] = None
    """Use defaults to create a map of default settings that will apply to all jobs in the workflow."""

    concurrency: Optional[Concurrency] = None
    """Use concurrency to ensure that only a single job or workflow using the same concurrency group will run at a time."""

    jobs: Optional[Dict[str, Job]] = None
    """A workflow run is made up of one or more jobs, which run in parallel by default."""

    def to_yaml(self) -> str:
        # Use model_dump to get the dictionary representation
        data = self.model_dump(by_alias=True)

        def remove_null_values(value):
            if isinstance(value, dict):
                return {
                    k: remove_null_values(v) for k, v in value.items() if v is not None
                }
            if isinstance(value, list):
                return [remove_null_values(v) for v in value]
            return value

        # Remove null values
        data = {k: remove_null_values(v) for k, v in data.items() if v is not None}

        # Convert the dictionary to a YAML string
        return yaml.dump(data, sort_keys=False, Dumper=_NoSingleQuotesDumper)


class _WorkflowProxy:
    _workflow: Optional[_Workflow]


def _ensure_workflow(f: _WorkflowProxy):
    """Utility class to set workflow if it does not exists."""
    if not hasattr(f, "_workflow"):
        f._workflow = _Workflow()


def _workflow_set_name(name: str):
    """Sets the name of the workflow."""

    def _(f: _WorkflowProxy):
        _ensure_workflow(f)
        f._workflow.name = name
        return f

    return _


def _workflow_set_run_name(run_name: str):
    """Sets the run_name of the workflow."""

    def _(f: _WorkflowProxy):
        _ensure_workflow(f)
        f._workflow.run_name = run_name
        return f

    return _


def _workflow_set_push_trigger_value(key: str, value):
    """Configure push trigger to automatically run the workflow."""

    def _(f: _WorkflowProxy):
        _ensure_workflow(f)
        if not hasattr(f._workflow, "on"):
            f._workflow.on = _Events()
        if not hasattr(f._workflow.on, "push"):
            f._workflow.on.push = PushEventTrigger()
        setattr(f._workflow.on.push, key, value)
        return f

    return _


def _workflow_set_permission(permission_name: str, permission_value: Permission):
    def _(f: _WorkflowProxy):
        _ensure_workflow(f)
        if not hasattr(f._workflow, "permissions"):
            f._workflow.permissions = Permissions()
        setattr(f._workflow.permissions, permission_name, permission_value)
        return f

    return _


def _workflow_set_env(key: str, value: str):
    def _(f: _WorkflowProxy):
        _ensure_workflow(f)
        if not hasattr(f._workflow, "env"):
            f._workflow.env = {}
        f._workflow.env[key] = value
        return f

    return _
