import lzma
import os
import tarfile

from pydantic import BaseModel, Field

from cli.app import CliApp
from archive.paths import get_output_dir_from_archive_path, get_prefix_from_archive_path
from clang.tags import DockerImageTags


class BuildCMakeArgs(BaseModel):
    """Build CMake that is necessary to build Clang."""

    cache_path: str = Field(..., description="Path where to store the cache.")

    host_gcc_path: str = Field(
        ...,
        description="Path to host compiler for compiling CMake.",
    )


class BuildCMakeApp(CliApp[BuildCMakeArgs]):
    """Build CMake that is necessary to build Clang."""

    def __init__(self):
        super().__init__("cmake")
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._cmake_dockerfile = "Dockerfile.cmake"
        self._host_gcc_path = os.path.join(self._build_path, "ci/gcc-x86_64-host")

    def _unpack_gcc_host(self):
        """Unpack GCC host compiler from cache."""

        self.logger.info(f"Unpacking {os.path.basename(self.args.host_gcc_path)}...")
        with lzma.open(self.args.host_gcc_path, "rb") as xz_file:
            with tarfile.open(fileobj=xz_file) as tar:
                tar.extractall(path=self._host_gcc_path, filter="tar")
        self.logger.info(
            f"Successfully unpacked {os.path.basename(self.args.host_gcc_path)}!"
        )

    def _build_cmake(self):
        """Builds cmake docker image."""

        self.logger.info(f"Building CMake...")
        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._cmake_dockerfile,
            tag=DockerImageTags.CMAKE,
            rm=True,
            decode=True,
            buildargs={
                "SRC_HOST_COMPILER_DIR": os.path.relpath(
                    os.path.join(
                        self._host_gcc_path,
                        get_prefix_from_archive_path(self.args.host_gcc_path),
                    ),
                    self._build_path,
                ),
                "INSTALL_DIR": get_output_dir_from_archive_path(self.args.cache_path),
            },
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"CMake was successfully built!")

    def _upload_artifacts(self):
        """Extracts sysroot from glibc image and stores it in the cache folder."""

        # Create container from glibc image to extract sysroot
        cmake_container = self.docker.containers.create(image=DockerImageTags.CMAKE)

        try:
            # Extract sysroot as archive
            os.makedirs(os.path.dirname(self.args.cache_path), exist_ok=True)
            self.logger.info(f"Storing cmake to cache at '{self.args.cache_path}'...")

            with lzma.open(self.args.cache_path, "wb") as output:
                chunks, _ = cmake_container.get_archive(
                    path=get_output_dir_from_archive_path(self.args.cache_path)
                )
                for chunk in chunks:
                    output.write(chunk)
            self.logger.info(
                f"linux_kernel+glibc stored to cache at '{self.args.cache_path}'!"
            )
        finally:
            # Cleanup container
            self.docker.api.remove_container(cmake_container.id)

    def run(self):
        self._unpack_gcc_host()
        self._build_cmake()
        self._upload_artifacts()


BuildCMakeApp.exec(__name__)
