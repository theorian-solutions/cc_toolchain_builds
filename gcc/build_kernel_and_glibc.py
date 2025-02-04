import lzma
import os

from pydantic import BaseModel, Field

from cc_common.cli import CliApp
from cc_common.pathutils import get_output_dir_from_archive_path
from gcc.tags import (
    GCC_TOOLCHAIN_LINUX_KERNEL_IMAGE_TAG,
    GCC_TOOLCHAIN_GLIBC_IMAGE_TAG,
)


class BuildKernelAndGlibcArgs(BaseModel):
    """Build linux kernel and glibc as a base for building cross compilers with hermetic sysroot."""

    cache_path: str = Field(..., description="Path where to store the cache.")

    linux_kernel_version: str = Field(
        ..., description="Version of linux kernel to build."
    )

    glibc_version: str = Field(..., description="Version of glibc to build.")


class BuildKernelAndGlibcApp(CliApp[BuildKernelAndGlibcArgs]):
    """Build linux kernel and glibc as a base for building cross compilers with hermetic sysroot."""

    def __init__(self):
        super().__init__("linux_kernel+glibc")
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._linux_kernel_dockerfile = "Dockerfile.kernel"
        self._linux_kernel_image_tag = GCC_TOOLCHAIN_LINUX_KERNEL_IMAGE_TAG
        self._glibc_dockerfile = "Dockerfile.glibc"
        self._glibc_image_tag = GCC_TOOLCHAIN_GLIBC_IMAGE_TAG

    @property
    def _linux_kernel_full_image_tag(self):
        """Returns docker image tag for linux kernel image containing both repository and version in format <repository>:<version>"""
        return f"{self._linux_kernel_image_tag}:{self.args.linux_kernel_version}"

    @property
    def _glibc_full_image_tag(self):
        """Returns docker image tag for glibc image containing both repository and version in format <repository>:<version>"""
        return f"{self._glibc_image_tag}:{self.args.glibc_version}"

    def _build_linux_kernel(self):
        """Builds linux kernel docker image."""

        self.logger.info(f"Building linux kernel v{self.args.linux_kernel_version}...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._linux_kernel_dockerfile,
            tag=self._linux_kernel_full_image_tag,
            rm=True,
            decode=True,
            buildargs={
                "INSTALL_DIR": get_output_dir_from_archive_path(self.args.cache_path),
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
            tag=self._glibc_full_image_tag,
            rm=True,
            decode=True,
            buildargs={
                "INSTALL_DIR": get_output_dir_from_archive_path(self.args.cache_path),
                "LINUX_KERNEL_VERSION": self.args.linux_kernel_version,
                "GLIBC_VERSION": self.args.glibc_version,
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"glibc was successfully built!")

    def _upload_artifacts(self):
        """Extracts sysroot from glibc image and stores it in the cache folder."""

        # Create container from glibc image to extract sysroot
        glibc_container = self.docker.containers.create(
            image=self._glibc_full_image_tag
        )

        try:
            # Extract sysroot as archive
            self.logger.info(
                f"Storing linux_kernel+glibc to cache at '{self.args.cache_path}'..."
            )

            with lzma.open(self.args.cache_path, "wb") as output:
                chunks, _ = glibc_container.get_archive(
                    path=get_output_dir_from_archive_path(self.args.cache_path)
                )
                for chunk in chunks:
                    output.write(chunk)
            self.logger.info(
                f"linux_kernel+glibc stored to cache at '{self.args.cache_path}'!"
            )
        finally:
            # Cleanup container
            self.docker.api.remove_container(glibc_container.id)

    def run(self):
        self._build_linux_kernel()
        self._build_glibc()
        self._upload_artifacts()


BuildKernelAndGlibcApp.exec(__name__)
