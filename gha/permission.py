from typing import Literal, Optional, Union

from gha.core import GhaModel

Permission = Union[Literal["read"], Literal["write"]]
"""Access level."""


class Permissions(GhaModel):
    """Permits the workflow to access or execute specific actions."""

    actions: Optional[Permission] = None
    """Work with GitHub Actions. For example, actions: write permits an action to cancel a workflow run."""

    attestations: Optional[Permission] = None
    """Work with artifact attestations. For example, attestations: write permits an action to generate an artifact attestation for a build."""

    checks: Optional[Permission] = None
    """Work with check runs and check suites. For example, checks: write permits an action to create a check run."""

    contents: Optional[Permission] = None
    """Work with the contents of the repository. For example, contents: read permits an action to list the commits, and contents: write allows the action to create a release."""

    deployments: Optional[Permission] = None
    """Work with deployments. For example, deployments: write permits an action to create a new deployment."""

    discussions: Optional[Permission] = None
    """Work with GitHub Discussions. For example, discussions: write permits an action to close or delete a discussion."""

    id_token: Optional[Permission] = None
    """Fetch an OpenID Connect (OIDC) token. This requires id-token: write."""

    issues: Optional[Permission] = None
    """Work with issues. For example, issues: write permits an action to add a comment to an issue."""

    packages: Optional[Permission] = None
    """Work with GitHub Packages. For example, packages: write permits an action to upload and publish packages on GitHub Packages."""

    pages: Optional[Permission] = None
    """Work with GitHub Pages. For example, pages: write permits an action to deploy updates to GitHub Pages."""

    pull_requests: Optional[Permission] = None
    """Work with pull requests. For example, pull-requests: write permits an action to merge pull requests."""

    repository_projects: Optional[Permission] = None
    """Work with repository projects. For example, repository-projects: write permits an action to create or update project boards."""

    security_events: Optional[Permission] = None
    """Work with security events. For example, security-events: write permits an action to create or update security alerts."""

    statuses: Optional[Permission] = None
    """Work with commit statuses. For example, statuses: write permits an action to create or update commit statuses."""
