from typing import List, Literal, Optional, Union

from gha.core import GhaModel


class BaseEvent(GhaModel):
    """Base class for events to inherit."""

    types: Optional[
        List[
            Union[
                Literal["created"],
                Literal["edited"],
                Literal["deleted"],
                Literal["types"],
            ]
        ]
    ] = None
    """Use to define the type of activity that will trigger a workflow run."""


class PushEventTrigger(BaseEvent):
    """Runs workflow when you push a commit or tag, or when you create a repository from a template."""

    branches: Optional[List[str]] = None
    """Filter to configure workflow to only run when specific branches are pushed."""

    branches_ignore: Optional[List[str]] = None
    """Filter to configure workflow to skip running when specific branches are pushed."""

    paths: Optional[List[str]] = None
    """Filter to configure workflow to only run when specific files are included in change."""

    tags: Optional[List[str]] = None
    """Filter to configure workflow to only run when specific tags are pushed."""

    tags_ignore: Optional[List[str]] = None
    """Filter to configure workflow to skip running when specific tags are pushed."""
