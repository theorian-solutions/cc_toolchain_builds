import os
from typing import Literal
import importlib

from pydantic import BaseModel, Field

from cli.app import CliApp


class BaseImageArgs(BaseModel):
    """Provides ability to either store or base docker images to/from cache."""

    toolchain: str = Field(
        ..., description="Name of the toolchain for which base image is loaded/stored."
    )

    cache_path: str = Field(..., description="Path where to store the cache.")

    op: Literal["load", "store"] = Field(
        ..., description="Which operation to use - 'load' or 'store'."
    )


class BaseImageApp(CliApp[BaseImageArgs]):
    """Provides ability to either store or load base docker images to/from cache."""

    def __init__(self):
        super().__init__("base-image-builder")
        self._build_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            self.args.toolchain,
        )
        self._dockerfile = "Dockerfile.base"
        tags = importlib.import_module(f"{self.args.toolchain}.tags")
        self._image_tag = getattr(tags, "DockerImageTags").BASE

    def run(self):
        if self.args.op == "load":
            self._load_cache()
        else:
            self._store_cache()

    def _load_cache(self):
        # Calculate tarball path
        image_path = os.path.join(self.args.cache_path, f"{self._image_tag}.tar")
        self.logger.info(
            f"Loading image '{self._image_tag}' from cache at '{image_path}'..."
        )

        # Load image tarball into memory
        image_cache = bytes()
        with open(image_path, "rb") as image_cache_file:
            image_cache = image_cache_file.read()

        # Load image into docker env
        image = self.docker.images.load(data=image_cache)[0]
        if not image.tag(repository=self._image_tag, tag="latest"):
            raise RuntimeError(f"Failed to set the tag for image '{self._image_tag}'!")

        self.logger.info(f"Image '{self._image_tag}' loaded successfully!")

    def _store_cache(self):
        # Create cache path if it does not exists
        os.makedirs(self.args.cache_path, exist_ok=True)

        self.logger.info(f"Building image '{self._image_tag}'...")

        response = self.docker.api.build(
            path=self._build_path,
            dockerfile=self._dockerfile,
            tag=self._image_tag,
            rm=True,
            decode=True,
        )
        for chunk in response:
            if "stream" in chunk:
                self.logger.info(chunk["stream"].strip())
            if "error" in chunk:
                raise RuntimeError(chunk["error"].strip())
        self.logger.info(f"Image '{self._image_tag}' built successfully!")

        # Store image to cache
        output_path = os.path.join(self.args.cache_path, f"{self._image_tag}.tar")
        self.logger.info(
            f"Storing image '{self._image_tag}' to cache at '{output_path}'..."
        )
        with open(output_path, "wb") as output:
            for chunk in self.docker.images.get(self._image_tag).save():
                output.write(chunk)
        self.logger.info(
            f"Image '{self._image_tag}' stored to cache at '{output_path}' successfully!"
        )


BaseImageApp.exec(__name__)
