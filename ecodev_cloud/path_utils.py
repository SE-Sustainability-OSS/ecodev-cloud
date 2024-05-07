from pathlib import Path


def forge_key(file_path: Path) -> str:
    """
    Form a valid cloud key out of the passed file_path
     (basically trailing the leading ecodev_cloud/ parent)
    """
    return str(file_path.relative_to(*file_path.parts[:2]))


ROOT_DIRECTORY = Path('/app')
