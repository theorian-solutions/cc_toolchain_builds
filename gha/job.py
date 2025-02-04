from typing import Dict, List, Literal, Optional, Union

from pydantic import Field

from gha.core import GhaModel
from gha.git import CheckoutActionV4
from gha.permission import Permissions
from gha.shell import ShellAction, ShellKind

Step = Union[ShellAction, CheckoutActionV4]
"""Available steps in job."""


class DefaultShellActionStepSettings(GhaModel):
    """Settings for default shell and working-directory to all run steps in the job."""

    shell: Optional[ShellKind] = None
    """The shell to use for running the command."""

    working_directory: Optional[str] = None
    """The working directory for the step."""


class DefaultStepSettings(GhaModel):
    """Available settings that for applying to all steps in the job."""

    run: Optional[DefaultShellActionStepSettings] = None
    """Provide default shell and working-directory to all run steps in the job."""


JobConfigurationMatrix = Union[
    Dict[
        Union[
            Literal[
                "include"
            ],  # Expand existing matrix configurations or to add new configurations.
            Literal[
                "exclude"
            ],  # Use to remove specific configurations defined in the matrix.
        ],
        List[Dict[str, Union[str, int]]],
    ],
    Dict[str, List[Union[int, str]]],
]
"""Holds a matrix of different job configurations."""


class Concurrency(GhaModel):
    """Set options to allow running only a single job or workflow using the same concurrency group at time."""

    group: str = ""
    """Group name/identifier."""

    cancel_in_progress: Optional[bool] = None
    """Set to true to also cancel any currently running job or workflow in the same concurrency group."""


class JobStrategy(GhaModel):
    """Provides ability to set a matrix strategy for your job."""

    matrix: Optional[JobConfigurationMatrix] = None
    """Define a matrix of different job configurations."""

    fail_fast: Optional[bool] = None
    """If true GitHub will cancel all in-progress and queued jobs in the matrix if any job in the matrix fails."""

    max_parallel: Optional[int] = None
    """Set the maximum number of jobs that can run simultaneously"""


class ContainerCredentials(GhaModel):
    """Setup credentials to pull the image."""

    username: str = ""
    """Docker registry account username."""

    password: str = ""
    """Docker registry account password."""


class Container(GhaModel):
    """Used to setup docker container to run any steps in a job that don't already specify a container."""

    image: str = ""
    """Define the Docker image to use as the container to run the action."""

    credentials: Optional[ContainerCredentials] = None
    """Use if the image's container registry requires authentication to pull the image."""

    env: Optional[Dict[str, str]] = None
    """Use to set a map of environment variables in the container."""

    ports: Optional[List[int]] = None
    """Use to set an array of ports to expose on the container."""

    volumes: Optional[List[str]] = None
    """Use to set an array of volumes for the container to use."""

    options: Optional[Union[str, List[str]]]
    """Use to configure additional Docker container resource options."""


class Job(GhaModel):
    """Allows to configure each job in your GitHub Actions workflow."""

    name: Optional[str] = None
    """A descriptive name for the job."""

    runs_on: Optional[Union[str, List[str]]] = None
    """The type of runner to run the job on."""

    needs: Optional[List[str]] = None
    """A list of jobs that must complete successfully before this job runs."""

    exec_if: Optional[str] = Field(serialization_alias="if", default=None)
    """A conditional expression that determines whether the job runs."""

    permissions: Optional[Permissions] = None
    """Permissions for the job, which can be set at the job level."""

    environment: Optional[Union[str, Dict[str, str]]] = None
    """The environment to run the job in."""

    concurrency: Optional[Concurrency] = None
    """Controls the concurrency of the job."""

    outputs: Optional[Dict[str, str]] = None
    """A map of outputs for the job."""

    env: Optional[Dict[str, str]] = None
    """A map of environment variables to set for the job."""

    default: Optional[DefaultStepSettings] = None
    """Map of default settings that will apply to all steps in the job"""

    steps: Optional[List[Step]] = None
    """A list of steps to run in the job."""

    timeout_minutes: Optional[int] = None
    """The maximum time to run the job before it is automatically cancelled."""

    strategy: Optional[JobStrategy] = None
    """Defines a matrix of different configurations to run the job."""

    continue_on_error: Optional[bool] = None
    """Whether to continue running the job if a step fails."""

    container: Optional[Union[str, Container]] = None
    """The container to run the job in."""

    services: Optional[Dict[str, Container]] = None
    """A map of services to run with the job."""

    uses: Optional[str] = None
    """The location and version of a reusable workflow file to run as a job."""

    with_options: Optional[Dict[str, str]] = Field(
        serialization_alias="with", default=None
    )
    """Provide a map of inputs that are passed to the reusable workflow."""

    secrets: Optional[Union[Literal["inherit"], Dict[str, str]]] = None
    """When a job is used to call a reusable workflow, you can use secrets to provide a map of secrets that are passed to the called workflow."""
