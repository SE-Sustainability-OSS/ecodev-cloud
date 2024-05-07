"""
Module implementing disk helper methods (centered around pathlib)
"""
import shutil
from pathlib import Path
from typing import Iterator


def disk_is_dir(file_path: Path) -> bool:
    """
    Check if a disk file_path is a folder or not
    """
    return file_path.is_dir()


def disk_rglob(file_path: Path, pattern: str | None = None) -> Iterator[Path]:
    """
    Rglob functionality: recursively find all files in the file_path folder having passed pattern
    """
    yield from sorted(list(file_path.rglob(pattern or '*')))


def disk_iterdir(file_path: Path) -> Iterator[Path]:
    """
    list all files and folders directly in the disk file_path folder.
    """
    yield from sorted(list(file_path.iterdir()))


def disk_exists(file_path: Path) -> bool:
    """
    Check if a file_path exists on disk
    """
    return file_path.exists()


def disk_copy(origin: Path, dest: Path) -> None:
    """
    Copy a disk origin path to a disk destination path
    """
    shutil.copy(str(origin), str(dest))


def disk_move(origin: Path, dest: Path) -> None:
    """
    Move a disk origin path to a disk destination path
    """
    shutil.move(str(origin), str(dest))
