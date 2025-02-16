import lzma
import os
import requests
import tarfile
from typing import Optional
import psutil

from pydantic import Field, ValidationInfo, field_validator

from archive.paths import (
    get_prefix_from_archive_path,
    get_output_dir_from_archive_path,
)
from clang.tags import DockerImageTags
from toolchain.base import ToolchainBaseArgs, ToolchainBaseApp


class BuildClangArgs(ToolchainBaseArgs):
    """Build Clang cross compiler with hermetic sysroot."""

    sysroot_path: str = Field(..., description="Path to sysroot archive.")

    cmake_path: str = Field(..., description="Path to cmake archive.")

    llvm_version: str = Field(..., description="Version of LLVM+Clang to build.")

    llvm_enable_projects: str = Field(
        ...,
        description="Semicolon separated list of projects to build. Dependant on LLVM version.",
    )

    llvm_enable_runtimes: Optional[str] = Field(
        default="",
        description="Semicolon separated list of runtimes to build. Dependant on LLVM version.",
    )

    host_clang_version: Optional[str] = Field(
        default=None,
        description="If provided it will use already uploaded Clang as host compiler to build current Clang compiler.",
    )

    host_gcc_path: Optional[str] = Field(
        ...,
        description="Path to host GCC compiler to use when host clang version not provided.",
    )

    @field_validator("host_gcc_path", mode="after")
    @classmethod
    def check_host_compiler_provided(
        cls, value: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        if (not value and not info.data["host_clang_version"]) or (
            value and info.data["host_clang_version"]
        ):
            raise ValueError(
                "Either `--host-clang-version` or `--host-gcc-path` must be provided! "
                f"Got --host-clang-version={value} and --host_clang_version={info.data["host_clang_version"]}"
            )
        return value


class BuildClangApp(ToolchainBaseApp[BuildClangArgs]):
    """Build Clang cross compiler with hermetic sysroot."""

    def __init__(self):
        super().__init__("clang", DockerImageTags.CLANG)
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._clang_dockerfile = "Dockerfile.clang"
        self._sysroot_path = os.path.join(self._build_path, "ci/sysroot")
        self._host_gcc_path = os.path.join(self._build_path, "ci/gcc-x86_64-host")
        self._host_clang_path = os.path.join(self._build_path, "ci/clang-x86_64-host")
        self._cmake_path = os.path.join(self._build_path, "ci/cmake")

    @property
    def _release_asset_name(self):
        """Returns Clang artifact name as uploaded to release artifacts."""
        return f"clang+llvm-{self.args.llvm_version}-x86_64-linux-gnu.tar.xz"

    @property
    def _host_clang_asset_name(self):
        """Returns host Clang artifact name as uploaded to release artifacts."""
        return f"clang+llvm-{self.args.host_clang_version}-x86_64-linux-gnu.tar.xz"

    @property
    def _is_host_gcc(self) -> bool:
        """Checks if GCC is used as host compiler to compile Clang."""
        return not self.args.host_clang_version

    def _unpack_cmake(self):
        """Unpack cmake from cache."""

        self.logger.info(f"Unpacking {os.path.basename(self.args.cmake_path)}...")
        with lzma.open(self.args.cmake_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._cmake_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.cmake_path)}!"
        )

    def _unpack_sysroot(self):
        """Unpack sysroot from cache."""

        self.logger.info(f"Unpacking {os.path.basename(self.args.sysroot_path)}...")
        with lzma.open(self.args.sysroot_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._sysroot_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.sysroot_path)}!"
        )

    def _unpack_gcc_host(self):
        """Unpack GCC host compiler from cache."""

        if not self.args.host_gcc_path:
            raise RuntimeError(
                "Requested unpacking of host GCC, but 'host-gcc-path' argument not provided!"
            )

        self.logger.info(f"Unpacking {os.path.basename(self.args.host_gcc_path)}...")
        with lzma.open(self.args.host_gcc_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_gcc_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.host_gcc_path)}!"
        )

    def _download_and_unpack_host_clang(self):
        """Downloads host compiler from GitHub release assets and unpacks it."""

        if not self.args.host_clang_version:
            raise RuntimeError(
                "Requested unpacking of host clang, but 'host-clang-version' argument not provided!"
            )

        host_clang_asset = next(
            (
                asset
                for asset in self._release_assets
                if asset.name == self._host_clang_asset_name
            ),
            None,
        )
        if host_clang_asset is None:
            raise RuntimeError(
                f"Could not find host Clang compiler '{self._host_clang_asset_name}' in release assets!"
            )

        self.logger.info(
            f"Downloading host Clang compiler '{host_clang_asset.name}'..."
        )
        response = requests.get(host_clang_asset.browser_download_url, stream=True)
        host_clang_download_path = os.path.join("/tmp", host_clang_asset.name)
        with open(host_clang_download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        self.logger.info(
            f"Host Clang compiler '{host_clang_asset.name}' successfully downloaded!"
        )

        self.logger.info(f"Unpacking '{host_clang_asset.name}'...")
        with lzma.open(host_clang_download_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_clang_path, filter="tar")
        self.logger.info(f"Successfully unpacked {host_clang_asset.name}!")

        # Cleanup downloaded archive as it is not needed anymore
        os.remove(host_clang_download_path)

    def _build_clang(self, host_compiler_path: str):
        """Builds Clang by using provided host compiler."""

        self.logger.info(f"Building clang-{self.args.llvm_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._clang_dockerfile,
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
                "SRC_CMAKE_DIR": os.path.relpath(
                    os.path.join(
                        self._sysroot_path,
                        get_prefix_from_archive_path(self.args.cmake_path),
                    ),
                    self._build_path,
                ),
                "SRC_HOST_COMPILER_DIR": os.path.relpath(
                    host_compiler_path, self._build_path
                ),
                "PARALLEL_COMPILE_JOBS": psutil.cpu_count(logical=False),
                "PARALLEL_LINK_JOBS": psutil.virtual_memory().total
                // (15 * 1024**3),  # 1 Link job per 15GB of RAM
                "ENABLE_PROJECTS": self.args.llvm_enable_projects,
                "ENABLE_RUNTIMES": self.args.llvm_enable_runtimes,
                "ENABLE_LIBCXX": "OFF" if self._is_host_gcc else "ON",
                "INSTALL_DIR": get_output_dir_from_archive_path(self._release_assets),
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
        self._unpack_cmake()
        self._unpack_sysroot()

        if not self.args.host_clang_version:
            self._unpack_gcc_host()
            self._build_clang(
                os.path.join(
                    self._host_gcc_path,
                    get_prefix_from_archive_path(self.args.host_gcc_path),
                )
            )
        else:
            self._download_and_unpack_host_clang()
            self._build_clang(
                os.path.join(
                    self._host_clang_path,
                    get_prefix_from_archive_path(self._host_clang_asset_name),
                )
            )


BuildClangApp.exec(__name__)
