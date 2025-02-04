import lzma
import os
import requests
import tarfile
from typing import Optional

from pydantic import BaseModel, Field

from cc_common.cli import CliApp
from cc_common.pathutils import (
    get_prefix_from_archive_path,
    get_output_dir_from_archive_path,
)
from gcc.tags import GCC_TOOLCHAIN_IMAGE_TAG


class BuildGccArgs(BaseModel):
    """Build GCC cross compiler with hermetic sysroot."""

    repository: str = Field(..., description="The owner and repository name.")

    release_id: str = Field(
        ..., description="Id of the release where build artifact will be uploaded."
    )

    linux_kernel_glibc_path: str = Field(
        ..., description="Path to linux_kernel+glibc archive."
    )

    force_rebuild: bool = Field(
        ...,
        description="If set rebuilds and reuploads existing GCC builds for given release version (yes/no).",
    )

    gcc_version: str = Field(..., description="Version of GCC to build.")

    binutils_version: str = Field(..., description="Version of binutils to build.")

    host_gcc_version: Optional[str] = Field(
        default=None,
        description="If provided it will use already uploaded GCC as host compiler to build current GCC compiler.",
    )


class BuildGccApp(CliApp[BuildGccArgs]):
    """Build GCC cross compiler with hermetic sysroot."""

    def __init__(self):
        super().__init__("gcc")
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._gcc_dockerfile = "Dockerfile.gcc"
        self._gcc_no_host_dockerfile = "Dockerfile.gcc_no_host"
        self._gcc_image_tag = GCC_TOOLCHAIN_IMAGE_TAG
        self._release_cache = None
        self._release_artifacts_cache = None
        self._sysroot_path = os.path.join(self._build_path, "ci/linux_kernel+glibc")
        self._host_gcc_path = os.path.join(self._build_path, "ci/gcc-x86_64-host")

    @property
    def _gcc_full_image_tag(self):
        """Returns docker image tag for gcc image containing both repository and version in format <repository>:<version>"""
        return f"{self._gcc_image_tag}:{self.args.gcc_version}"

    @property
    def _gcc_asset_name(self):
        """Returns GCC artifact name as uploaded to release artifacts."""
        return f"gcc-{self.args.gcc_version}-x86_64-linux-gnu.tar.xz"

    @property
    def _host_gcc_asset_name(self):
        """Returns host GCC artifact name as uploaded to release artifacts."""
        return f"gcc-{self.args.host_gcc_version}-x86_64-linux-gnu.tar.xz"

    @property
    def _release(self):
        if self._release_cache is None:
            repo = self.github.get_repo(self.args.repository)
            self._release_cache = repo.get_release(self.args.release_id)
        return self._release_cache

    @property
    def _release_assets(self):
        if self._release_artifacts_cache is None:
            self._release_artifacts_cache = self._release.get_assets()
        return self._release_artifacts_cache

    def _check_if_already_exists(self):
        """Verifies if requested GCC version is already built and uploaded to release assets."""

        return (
            next(
                (
                    asset
                    for asset in self._release_assets
                    if asset.name == self._gcc_asset_name
                ),
                None,
            )
            is not None
        )

    def _unpack_sysroot(self):
        """Unpack linux_kernel+glibc from cache."""

        self.logger.info(
            f"Unpacking {os.path.basename(self.args.linux_kernel_glibc_path)}..."
        )
        with lzma.open(self.args.linux_kernel_glibc_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._sysroot_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.linux_kernel_glibc_path)}!"
        )

    def _download_and_unpack_host_gcc(self):
        """Downloads host compiler from GitHub release assets and unpacks it."""

        if not self.args.host_gcc_version:
            raise RuntimeError(
                "Requested unpacking of host gcc, but 'host-gcc-version' argument not provided!"
            )

        host_gcc_asset = next(
            (
                asset
                for asset in self._release_assets
                if asset.name == self._host_gcc_asset_name
            ),
            None,
        )
        if host_gcc_asset is None:
            raise RuntimeError(
                f"Could not find host GCC compiler '{self._host_gcc_asset_name}' in release assets!"
            )

        self.logger.info(f"Downloading host GCC compiler '{host_gcc_asset.name}'...")
        response = requests.get(host_gcc_asset.browser_download_url, stream=True)
        host_gcc_download_path = os.path.join("/tmp", host_gcc_asset.name)
        with open(host_gcc_download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        self.logger.info(
            f"Host GCC compiler '{host_gcc_asset.name}' successfully downloaded!"
        )

        self.logger.info(f"Unpacking '{host_gcc_asset.name}'...")
        with lzma.open(host_gcc_download_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_gcc_path, filter="tar")
        self.logger.info(f"Successfully unpacked {host_gcc_asset.name}!")

        # Cleanup downloaded archive as it is not needed anymore
        os.remove(host_gcc_download_path)

    def _build_gcc_no_host(self):
        """Builds GCC by using system provided compiler."""

        self.logger.info(f"Building gcc-{self.args.gcc_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._gcc_no_host_dockerfile,
            tag=self._gcc_full_image_tag,
            rm=True,
            decode=True,
            buildargs={
                "SRC_SYSROOT_DIR": os.path.relpath(
                    os.path.join(
                        self._sysroot_path,
                        get_prefix_from_archive_path(self.args.linux_kernel_glibc_path),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(self._gcc_asset_name),
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

        if not self.args.host_gcc_version:
            raise RuntimeError(
                "Requested building with host gcc, but 'host-gcc-version' argument not provided!"
            )

        self.logger.info(f"Building gcc-{self.args.gcc_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._gcc_dockerfile,
            tag=self._gcc_full_image_tag,
            rm=True,
            decode=True,
            buildargs={
                "SRC_HOST_GCC_DIR": os.path.relpath(
                    os.path.join(
                        self._host_gcc_path,
                        get_prefix_from_archive_path(self._host_gcc_asset_name),
                    ),
                    self._build_path,
                ),
                "SRC_SYSROOT_DIR": os.path.relpath(
                    os.path.join(
                        self._sysroot_path,
                        get_prefix_from_archive_path(self.args.linux_kernel_glibc_path),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(self._gcc_asset_name),
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

    def _upload_artifacts(self):
        """Extracts sysroot from gcc image and uploads it to release assets."""

        # Create container from gcc image to extract sysroot
        gcc_container = self.docker.containers.create(image=self._gcc_full_image_tag)

        try:
            # Extract sysroot as archive
            archive_path = os.path.join("/tmp", self._gcc_asset_name)
            self.logger.info(
                f"Extracting gcc-{self.args.gcc_version} from image to '{archive_path}'..."
            )

            with lzma.open(archive_path, "wb") as output:
                chunks, _ = gcc_container.get_archive(
                    path=get_output_dir_from_archive_path(self._gcc_asset_name),
                )
                for chunk in chunks:
                    output.write(chunk)
            self.logger.info(
                f"Successfully extracted gcc-{self.args.gcc_version} to '{archive_path}'!"
            )

            # Upload to release assets
            self.logger.info(f"Uploading {self._gcc_asset_name} to GitHub release")
            asset = self._release.upload_asset(
                path=archive_path, content_type="application/x-xz-compressed-tar"
            )
            self.logger.info(
                f"Asset {self._gcc_asset_name} successfully uploaded to GitHub release (id={asset.id})!"
            )

        finally:
            # Cleanup container
            self.docker.api.remove_container(gcc_container.id)

    def run(self):
        if self.args.force_rebuild:
            self.logger.warning(
                "Flag 'force-rebuild' used, discarding any already built and uploaded GCC artifact!"
            )
        elif not self._check_if_already_exists():
            self.logger.warning("No existing GCC artifact found in GitHub releases!")
        else:
            self.logger.info(
                "GCC already built and published to GitHub releases. Skipping this step..."
            )
            return

        self._unpack_sysroot()

        if not self.args.host_gcc_version:
            self._build_gcc_no_host()
        else:
            self._download_and_unpack_host_gcc()
            self._build_gcc_with_host()
        self._upload_artifacts()


BuildGccApp.exec(__name__)
