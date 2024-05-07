"""
module implementing helper methods for migration to azure blob storage
"""
from pathlib import Path
from typing import Callable
from typing import Iterator

from ecodev_core import logger_get

from ecodev_cloud.disk.disk_helpers import disk_exists
from ecodev_cloud.disk.disk_loader import disk_load
from ecodev_cloud.disk.disk_saver import disk_save


log = logger_get(__name__)
TRANSFER_IDX = 'transferred_files.json'
FAILED_IDX = 'failed_files.json'


def to_blob(folders: list[Path],
            file_transferer: Callable[[Path], None],
            folder_scanner: Callable[[Path], Iterator[Path]],
            index_folder: Path,
            dir_checker: Callable[[Path], bool]
            ) -> None:
    """
    Robust migration from all content (in folders paths) to Azure blob storage.
    """
    for folder in folders:
        _transfer_all(folder, _load_index(TRANSFER_IDX, index_folder), _load_index(
            FAILED_IDX, index_folder), file_transferer, folder_scanner, index_folder, dir_checker)


def _transfer_all(folder: Path,
                  ok_files: set[Path],
                  ko_files: set[Path],
                  file_transferer: Callable[[Path], None],
                  folder_scanner: Callable[[Path], Iterator[Path]],
                  index_folder: Path,
                  dir_checker: Callable[[Path], bool]
                  ) -> None:
    """
    Transfer all files in folder from folder to Azure blob storage if not in ok_files | ko_files.
    """
    log.info(f'Transferring all files from {folder}')
    files_to_transfer = [fp for fp in folder_scanner(folder) if fp not in ok_files | ko_files]

    for file_path in [fp for fp in files_to_transfer if not dir_checker(fp)]:
        try:
            file_transferer(file_path)
            ok_files.add(file_path)
        except Exception as e:
            log.critical(f'transferring {file_path.name} failed: {e} happened')
            ko_files.add(file_path)

    disk_save(index_folder / TRANSFER_IDX, [str(x) for x in ok_files])
    disk_save(index_folder / FAILED_IDX, [str(x) for x in ko_files])
    log.info(f'Successfully transferred all files from {folder}')


def _load_index(filename: str, index_folder: Path) -> set[Path]:
    """
    Load from disk the index consisting of all already transferred or failed files (filename given).
    """
    if disk_exists(file_path := index_folder / filename):
        return set(Path(x) for x in disk_load(file_path))

    return set()
