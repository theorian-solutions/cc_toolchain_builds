from typing import Literal, Optional

from pydantic import Field

from gha.core import GhaModel
from gha.step import StepBase


class CheckoutActionV4Options(GhaModel):
    """Options for CheckoutActionV4"""

    repository: Optional[str] = None
    """Repository name with owner. For example, actions/checkout
       Default: ${{ github.repository }}"""

    ref: Optional[str] = None
    """The branch, tag or SHA to checkout. When checking out the repository that
       triggered a workflow, this defaults to the reference or SHA for that event.
       Otherwise, uses the default branch."""

    token: Optional[str] = None
    """Personal access token (PAT) used to fetch the repository. The PAT is configured
       with the local git config, which enables your scripts to run authenticated git
       commands. The post-job step removes the PAT.

       We recommend using a service account with the least permissions necessary. Also
       when generating a new PAT, select the least scopes necessary.

       [Learn more about creating and using encrypted secrets](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets)

       Default: ${{ github.token }}"""

    ssh_key: Optional[str] = None
    """SSH key used to fetch the repository. The SSH key is configured with the local
       git config, which enables your scripts to run authenticated git commands. The
       post-job step removes the SSH key.

       We recommend using a service account with the least permissions necessary.

       [Learn more about creating and using encrypted secrets](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets)"""

    ssh_known_hosts: Optional[str] = None
    """Known hosts in addition to the user and global host key database. The public SSH
       keys for a host may be obtained using the utility `ssh-keyscan`. For example,
       `ssh-keyscan github.com`. The public key for github.com is always implicitly
       added."""

    ssh_strict: Optional[bool] = None
    """Whether to perform strict host key checking. When true, adds the options
       `StrictHostKeyChecking=yes` and `CheckHostIP=no` to the SSH command line. Use
       the input `ssh-known-hosts` to configure additional hosts.
       Default: true"""

    ssh_user: Optional[str] = None
    """The user to use when connecting to the remote SSH host. By default 'git' is
       used.
       Default: git"""

    persist_credentials: Optional[bool] = None
    """Whether to configure the token or SSH key with the local git config
       Default: true"""

    path: Optional[str] = None
    """Relative path under $GITHUB_WORKSPACE to place the repository"""

    clean: Optional[bool] = None
    """Whether to execute `git clean -ffdx && git reset --hard HEAD` before fetching
       Default: true"""

    filter: Optional[str] = None
    """Partially clone against a given filter. Overrides sparse-checkout if set.
       Default: null"""

    sparse_checkout: Optional[str] = None
    """Do a sparse checkout on given patterns. Each pattern should be separated with
       new lines.
       Default: null"""

    sparse_checkout_cone_mode: Optional[bool] = None
    """Specifies whether to use cone-mode when doing a sparse checkout.
       Default: true"""

    fetch_depth: Optional[int] = None
    """Number of commits to fetch. 0 indicates all history for all branches and tags.
       Default: 1"""

    fetch_tags: Optional[bool] = None
    """Whether to fetch tags, even if fetch-depth > 0.
       Default: false"""

    show_progress: Optional[bool] = None
    """Whether to show progress status output when fetching.
       Default: true"""

    lfs: Optional[bool] = None
    """Whether to download Git-LFS files
       Default: false"""

    submodules: Optional[bool] = None
    """Whether to checkout submodules: `true` to checkout submodules or `recursive` to
       recursively checkout submodules.

       When the `ssh-key` input is not provided, SSH URLs beginning with
       `git@github.com:` are converted to HTTPS.

       Default: false"""

    set_safe_directory: Optional[bool] = None
    """Add repository path as safe.directory for Git global config by running `git
       config --global --add safe.directory <path>`
       Default: true"""

    github_server_url: Optional[str] = None
    """The base URL for the GitHub instance that you are trying to clone from, will use
       environment defaults to fetch from the same instance that the workflow is
       running from unless specified. Example URLs are https://github.com or
       https://my-ghes-server.example.com"""


class CheckoutActionV4(StepBase):
    """This action checks-out your repository under $GITHUB_WORKSPACE, so your workflow can access it."""

    uses: Literal["actions/checkout@v4"] = "actions/checkout@v4"
    """Specifies an action to run."""

    with_options: Optional[CheckoutActionV4Options] = Field(
        serialization_alias="with", default=None
    )
    """A map of inputs to the action."""
