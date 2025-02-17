import lzma
import os
import tarfile
from typing import Optional

from pydantic import Field

from archive.paths import (
    get_prefix_from_archive_path,
    get_output_dir_from_archive_path,
)
from clang.tags import DockerImageTags
from toolchain.base import ToolchainBaseArgs, ToolchainBaseApp


class BuildClangArgs(ToolchainBaseArgs):
    """Build Clang cross compiler with hermetic sysroot."""

    sysroot_path: str = Field(..., description="Path to sysroot archive.")

    llvm_version: str = Field(..., description="Version of LLVM+Clang to build.")

    host_llvm: Optional[str] = Field(
        ...,
        description="Path to host LLVM to use to compile current Clang compiler.",
    )


class BuildClangApp(ToolchainBaseApp[BuildClangArgs]):
    """Build Clang cross compiler with hermetic sysroot."""

    def __init__(self):
        super().__init__("clang", DockerImageTags.CLANG)
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._clang_single_stage_dockerfile = "Dockerfile.clang_single_stage"
        self._clang_two_stage_dockerfile = "Dockerfile.clang_two_stage"
        self._sysroot_path = os.path.join(self._build_path, "ci/sysroot")
        self._host_clang_path = os.path.join(self._build_path, "ci/clang-x86_64-host")

    @property
    def _release_asset_name(self):
        """Returns Clang artifact name as uploaded to release artifacts."""
        return f"clang+llvm-{self.args.llvm_version}-x86_64-linux-gnu.tar.xz"

    def _unpack_sysroot(self):
        """Unpack sysroot from cache."""

        self.logger.info(f"Unpacking {os.path.basename(self.args.sysroot_path)}...")
        with lzma.open(self.args.sysroot_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._sysroot_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.sysroot_path)}!"
        )

    def _unpack_host_clang(self):
        """Unpacks given host LLVM archive."""

        if not self.args.host_llvm:
            raise RuntimeError(
                "Requested unpacking of host clang, but 'host-llvm' argument not provided!"
            )

        self.logger.info(f"Unpacking '{self.args.host_llvm}'...")
        with lzma.open(self.args.host_llvm, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_clang_path, filter="tar")
        self.logger.info(f"Successfully unpacked {self.args.host_llvm}!")

    def _build_clang_single_stage(self):
        """Builds Clang by using provided host Clang compiler."""

        if not self.args.host_llvm:
            raise RuntimeError(
                "Requested building with host clang, but 'host-llvm' argument not provided!"
            )

        self.logger.info(f"Building clang-{self.args.llvm_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._clang_single_stage_dockerfile,
            tag=DockerImageTags.CLANG,
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
                "SRC_HOST_COMPILER_DIR": os.path.relpath(
                    os.path.join(
                        self._host_clang_path,
                        get_prefix_from_archive_path(self.args.host_llvm),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(
                    self._release_asset_name
                ),
                "LLVM_VERSION": self.args.llvm_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"clang-{self.args.llvm_version} was successfully built!")

    def _build_clang_two_stage(self):
        """
        Builds Clang using host GCC provided by Ubuntu 18.04 in first stage
        and then uses built Clang to build Clang in second stage which is final output.
        """

        self.logger.info(f"Building clang-{self.args.llvm_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._clang_two_stage_dockerfile,
            tag=DockerImageTags.CLANG,
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
                "LLVM_VERSION": self.args.llvm_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"clang-{self.args.llvm_version} was successfully built!")

    def _build_toolchain(self):
        self._unpack_sysroot()

        if not self.args.host_llvm:
            self._build_clang_two_stage()
        else:
            self._unpack_host_clang()
            self._build_clang_single_stage()


BuildClangApp.exec(__name__)
