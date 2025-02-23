import lzma
import os
import tarfile

from pydantic import Field

from archive.paths import (
    get_prefix_from_archive_path,
    get_output_dir_from_archive_path,
)
from clang.tags import DockerImageTags
from toolchain.base import ToolchainBaseArgs, ToolchainBaseApp


class BuildLibClangArgs(ToolchainBaseArgs):
    """Build libclang for usage with clang.cindex python bindings."""

    llvm_version: str = Field(..., description="Version of LLVM+Clang to build.")

    compiler: str = Field(
        ...,
        description="Path to Clang compiler.",
    )


class BuildLibClangApp(ToolchainBaseApp[BuildLibClangArgs]):
    """Build libclang for usage with clang.cindex python bindings."""

    def __init__(self):
        super().__init__("libclang", DockerImageTags.LIBCLANG)
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._libclang_dockerfile = "Dockerfile.libclang"
        self._host_clang_path = os.path.join(self._build_path, "ci/clang-x86_64-host")

    @property
    def _release_asset_name(self):
        """Returns libclang artifact name as uploaded to release artifacts."""
        return f"libclang-{self.args.llvm_version}-x86_64-linux-gnu.tar.xz"

    def _unpack_host_clang(self):
        """Unpacks given host Clang archive."""

        self.logger.info(f"Unpacking '{self.args.compiler}'...")
        with lzma.open(self.args.compiler, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_clang_path, filter="tar")
        self.logger.info(f"Successfully unpacked {self.args.compiler}!")

    def _build_libclang(self):
        """Builds libclang by using provided host Clang compiler."""

        self.logger.info(f"Building libclang-{self.args.llvm_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._libclang_dockerfile,
            tag=DockerImageTags.LIBCLANG,
            rm=True,
            decode=True,
            buildargs={
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

    def _build_toolchain(self):
        self._unpack_host_clang()
        self._build_libclang()


BuildLibClangApp.exec(__name__)
