import lzma
import os
import tarfile
from typing import Optional

from pydantic import Field

from archive.paths import (
    get_prefix_from_archive_path,
    get_output_dir_from_archive_path,
)
from gcc.tags import DockerImageTags
from toolchain.base import ToolchainBaseArgs, ToolchainBaseApp


class BuildGccArgs(ToolchainBaseArgs):
    """Build GCC cross compiler with hermetic sysroot."""

    sysroot_path: str = Field(..., description="Path to sysroot archive.")

    gcc_version: str = Field(..., description="Version of GCC to build.")

    binutils_version: str = Field(..., description="Version of binutils to build.")

    host_gcc: Optional[str] = Field(
        default=None,
        description="Path to host GCC to use to compile current GCC compiler.",
    )


class BuildGccApp(ToolchainBaseApp[BuildGccArgs]):
    """Build GCC cross compiler with hermetic sysroot."""

    def __init__(self):
        super().__init__("gcc", DockerImageTags.GCC)
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._gcc_dockerfile = "Dockerfile.gcc"
        self._gcc_no_host_dockerfile = "Dockerfile.gcc_no_host"
        self._sysroot_path = os.path.join(self._build_path, "ci/sysroot")
        self._host_gcc_path = os.path.join(self._build_path, "ci/gcc-x86_64-host")

    @property
    def _release_asset_name(self):
        """Returns GCC artifact name as uploaded to release artifacts."""
        return f"gcc-{self.args.gcc_version}-x86_64-linux-gnu.tar.xz"

    def _unpack_sysroot(self):
        """Unpack sysroot from cache."""

        self.logger.info(f"Unpacking {os.path.basename(self.args.sysroot_path)}...")
        with lzma.open(self.args.sysroot_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._sysroot_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.sysroot_path)}!"
        )

    def _unpack_host_gcc(self):
        """Unpacks given host GCC archive."""

        if not self.args.host_gcc:
            raise RuntimeError(
                "Requested unpacking of host gcc, but 'host-gcc' argument not provided!"
            )

        self.logger.info(f"Unpacking '{self.args.host_gcc}'...")
        with lzma.open(self.args.host_gcc, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_gcc_path, filter="tar")
        self.logger.info(f"Successfully unpacked {self.args.host_gcc}!")

    def _build_gcc_no_host(self):
        """Builds GCC by using system provided compiler."""

        self.logger.info(f"Building gcc-{self.args.gcc_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._gcc_no_host_dockerfile,
            tag=DockerImageTags.GCC,
            rm=True,
            decode=True,
            buildargs={
                "SRC_SYSROOT_DIR": os.path.relpath(
                    os.path.join(
                        self._sysroot_path,
                        get_prefix_from_archive_path(self.args.sysroot_path),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(
                    self._release_asset_name
                ),
                "GCC_VERSION": self.args.gcc_version,
                "BINUTILS_VERSION": self.args.binutils_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"gcc-{self.args.gcc_version} was successfully built!")

    def _build_gcc_with_host(self):
        """Builds GCC by using provided host compiler."""

        if not self.args.host_gcc:
            raise RuntimeError(
                "Requested building with host gcc, but 'host-gcc-version' argument not provided!"
            )

        self.logger.info(f"Building gcc-{self.args.gcc_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._gcc_dockerfile,
            tag=DockerImageTags.GCC,
            rm=True,
            decode=True,
            buildargs={
                "SRC_HOST_GCC_DIR": os.path.relpath(
                    os.path.join(
                        self._host_gcc_path,
                        get_prefix_from_archive_path(self.args.host_gcc),
                    ),
                    self._build_path,
                ),
                "SRC_SYSROOT_DIR": os.path.relpath(
                    os.path.join(
                        self._sysroot_path,
                        get_prefix_from_archive_path(self.args.sysroot_path),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(self._release_assets),
                "GCC_VERSION": self.args.gcc_version,
                "BINUTILS_VERSION": self.args.binutils_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"gcc-{self.args.gcc_version} was successfully built!")

    def _build_toolchain(self):
        self._unpack_sysroot()

        if not self.args.host_gcc:
            self._build_gcc_no_host()
        else:
            self._unpack_host_gcc()
            self._build_gcc_with_host()


BuildGccApp.exec(__name__)
