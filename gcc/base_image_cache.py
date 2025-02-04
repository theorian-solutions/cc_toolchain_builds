import os
from typing import Literal

from pydantic import BaseModel, Field

from cc_common.cli import CliApp
from gcc.tags import (
    GCC_TOOLCHAIN_BASE_IMAGE_TAG,
    GCC_TOOLCHAIN_BASE_WITH_HOST_COMPILER_IMAGE_TAG,
)


class GccToolchainBaseImageArgs(BaseModel):
    """Provides ability to either store or load GCC toolchain base images to/from cache."""

    cache_path: str = Field(..., description="Path where to store the cache.")

    op: Literal["load", "store"] = Field(
        ..., description="Which operation to use - 'load' or 'store'."
    )


class GccToolchainBaseImageApp(CliApp[GccToolchainBaseImageArgs]):
    """Provides ability to either store or load GCC toolchain base images to/from cache."""

    def __init__(self):
        super().__init__("gcc-toolchain-base")
        self._build_path = os.path.dirname(os.path.abspath(__file__))
        self._gcc_toolchain_base_dockerfile = "Dockerfile.base"
        self._gcc_toolchain_base_image_tag = GCC_TOOLCHAIN_BASE_IMAGE_TAG
        self._gcc_toolchain_base_with_host_compiler_dockerfile = "Dockerfile.host_base"
        self._gcc_toolchain_base_image_with_host_compiler_tag = (
            GCC_TOOLCHAIN_BASE_WITH_HOST_COMPILER_IMAGE_TAG
        )

    def run(self):
        if self.args.op == "load":
            self._load_cache()
        else:
            self._store_cache()

    def _load_cache(self):
        images_to_load = [
            self._gcc_toolchain_base_image_tag,
            self._gcc_toolchain_base_image_with_host_compiler_tag,
        ]
        for image_tag in images_to_load:
            # Calculate tarball path
            image_path = os.path.join(self.args.cache_path, f"{image_tag}.tar")
            self.logger.info(
                f"Loading image '{image_tag}' from cache at '{image_path}'..."
            )

            # Load image tarball into memory
            image_cache = bytes()
            with open(image_path, "rb") as image_cache_file:
                image_cache = image_cache_file.read()

            # Load image into docker env
            image = self.docker.images.load(data=image_cache)[0]
            if not image.tag(repository=image_tag, tag="latest"):
                raise RuntimeError(f"Failed to set the tag for image '{image_tag}'!")

            self.logger.info(f"Image '{image_tag}' loaded successfully!")

    def _store_cache(self):
        # Create cache path if it does not exists
        os.makedirs(self.args.cache_path, exist_ok=True)

        images_to_build = [
            (self._gcc_toolchain_base_dockerfile, self._gcc_toolchain_base_image_tag),
            (
                self._gcc_toolchain_base_with_host_compiler_dockerfile,
                self._gcc_toolchain_base_image_with_host_compiler_tag,
            ),
        ]
        for dockerfile, image_tag in images_to_build:
            self.logger.info(f"Building image '{image_tag}'...")

            response = self.docker.api.build(
                path=self._build_path,
                dockerfile=dockerfile,
                tag=image_tag,
                rm=True,
                decode=True,
            )
            for chunk in response:
                if "stream" in chunk:
                    self.logger.info(chunk["stream"].strip())
                if "error" in chunk:
                    raise RuntimeError(chunk["error"].strip())
            self.logger.info(f"Image '{image_tag}' built successfully!")

            # Store image to cache
            output_path = os.path.join(self.args.cache_path, f"{image_tag}.tar")
            self.logger.info(
                f"Storing image '{image_tag}' to cache at '{output_path}'..."
            )
            with open(output_path, "wb") as output:
                for chunk in self.docker.images.get(image_tag).save():
                    output.write(chunk)
            self.logger.info(
                f"Image '{image_tag}' stored to cache at '{output_path}' successfully!"
            )


GccToolchainBaseImageApp.exec(__name__)
