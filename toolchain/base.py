from abc import ABC, abstractmethod
import lzma
import os
from typing import TypeVar

from pydantic import BaseModel, Field

from archive.paths import get_output_dir_from_archive_path
from cli.app import CliApp


class ToolchainBaseArgs(BaseModel):
    """Base class for arguments used to build toolchains."""

    repository: str = Field(..., description="The owner and repository name.")

    release_id: str = Field(
        ..., description="Id of the release where build artifact will be uploaded."
    )

    force_rebuild: bool = Field(
        ...,
        description="If set rebuilds and reuploads existing toolchain builds for given release version (yes/no).",
    )


TToolchainArgs = TypeVar("TToolchainArgs", bound=ToolchainBaseArgs)


class ToolchainBaseApp(CliApp[TToolchainArgs]):
    """Base class for CLI application used to build toolchain."""

    def __init__(self, name: str, toolchain_image_tag: str):
        super().__init__(name)
        self._image_tag = toolchain_image_tag
        self._release_cache = None
        self._release_artifacts_cache = None

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

    @property
    @abstractmethod
    def _release_asset_name(self) -> str:
        """Gets the name of the release asset that will be uploaded to GitHub releases"""

    def _check_if_already_exists(self):
        """Verifies if requested toolchain is already built and uploaded to release assets."""

        return (
            next(
                (
                    asset
                    for asset in self._release_assets
                    if asset.name == self._release_asset_name
                ),
                None,
            )
            is not None
        )

    def _upload_artifacts(self):
        """Extracts built toolchain and uploads it to release assets."""

        # Create container from built image to extract the output
        toolchain_container = self.docker.containers.create(image=self._image_tag)

        try:
            # Extract sysroot as archive
            archive_path = os.path.join("/tmp", self._release_asset_name)
            self.logger.info(
                f"Extracting ${self._image_tag} from image to '{archive_path}'..."
            )

            with lzma.open(archive_path, "wb") as output:
                chunks, _ = toolchain_container.get_archive(
                    path=get_output_dir_from_archive_path(self._release_asset_name),
                )
                for chunk in chunks:
                    output.write(chunk)
            self.logger.info(
                f"Successfully extracted ${self._image_tag} to '{archive_path}'!"
            )

            # Upload to release assets
            self.logger.info(f"Uploading {self._release_asset_name} to GitHub release")
            asset = self._release.upload_asset(
                path=archive_path, content_type="application/x-xz-compressed-tar"
            )
            self.logger.info(
                f"Asset {self._release_asset_name} successfully uploaded to GitHub release (id={asset.id})!"
            )

        finally:
            # Cleanup container
            self.docker.api.remove_container(toolchain_container.id)

    @abstractmethod
    def _build_toolchain(self):
        """
        Download dependencies and build toolchain using docker.

        Final image must have a tag provided through `toolchain_image_tag` constructor argument.
        """

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

        self._build_toolchain()

        self._upload_artifacts()
