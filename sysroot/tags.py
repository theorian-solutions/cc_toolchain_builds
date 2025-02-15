class DockerImageTags:
    """Contains tags for docker images built by this module."""

    BASE = "sysroot-toolchain-base"
    """Image tag for base image used by all other docker images."""

    LINUX_KERNEL = "sysroot-linux-kernel"
    """Image tag for intermediate linux kernel docker image."""

    SYSROOT = "sysroot"
    """Image tag for sysroot docker image."""
