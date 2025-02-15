import os


def get_prefix_from_archive_path(archive_path: str) -> str:
    """
    Calculates folder prefix that will be added based on archive filename.

    Args:
        archive_path: Relative or absolute path to the archive (must have two file extension .tar.<anything>).

    Returns: Prefix name of the root folder in archive.
    """

    tar_name, _ = os.path.splitext(os.path.basename(archive_path))
    prefix, _ = os.path.splitext(tar_name)
    return prefix


def get_output_dir_from_archive_path(archive_path: str) -> str:
    """
    Calculates sysroot output directory based on archive path that will be used to store the output.

    Args:
        archive_path: Relative or absolute path to the archive (must have two file extension .tar.<anything>).

    Returns: Absolute path where to store build outputs in Docker container.
    """

    return os.path.join("/var/buildlibs", get_prefix_from_archive_path(archive_path))
