import os

from pydantic import Field

from archive.paths import get_output_dir_from_archive_path
from sysroot.tags import DockerImageTags
from toolchain.base import ToolchainBaseApp, ToolchainBaseArgs


class BuildSysrootArgs(ToolchainBaseArgs):
    """Build linux kernel and glibc as a base for building cross compilers with hermetic sysroot."""

    linux_kernel_version: str = Field(
        ..., description="Version of linux kernel to build."
    )

    glibc_version: str = Field(..., description="Version of glibc to build.")


class BuildSysrootApp(ToolchainBaseApp[BuildSysrootArgs]):
    """Build linux kernel and glibc as a base for building cross compilers with hermetic sysroot."""

    def __init__(self):
        super().__init__("sysroot", DockerImageTags.SYSROOT)
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._linux_kernel_dockerfile = "Dockerfile.kernel"
        self._glibc_dockerfile = "Dockerfile.glibc"

    @property
    def _release_asset_name(self):
        """Returns sysroot artifact name as uploaded to release artifacts."""
        return f"sysroot-linux-kernel-{self.args.linux_kernel_version}+glibc-{self.args.glibc_version}-x86_64-linux-gnu.tar.xz"

    def _build_linux_kernel(self):
        """Builds linux kernel docker image."""

        self.logger.info(f"Building linux kernel v{self.args.linux_kernel_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._linux_kernel_dockerfile,
            tag=DockerImageTags.LINUX_KERNEL,
            rm=True,
            decode=True,
            buildargs={
                "INSTALL_DIR": get_output_dir_from_archive_path(
                    self._release_asset_name
                ),
                "LINUX_KERNEL_VERSION": self.args.linux_kernel_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"Linux kernel was successfully built!")

    def _build_glibc(self):
        """Builds glibc docker image."""

        self.logger.info(f"Building glibc v{self.args.glibc_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._glibc_dockerfile,
            tag=DockerImageTags.SYSROOT,
            rm=True,
            decode=True,
            buildargs={
                "INSTALL_DIR": get_output_dir_from_archive_path(
                    self._release_asset_name
                ),
                "GLIBC_VERSION": self.args.glibc_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"glibc was successfully built!")

    def _build_toolchain(self):
        self._build_linux_kernel()
        self._build_glibc()


BuildSysrootApp.exec(__name__)
