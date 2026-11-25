"""Create local run manifests without embedding dataset contents."""
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess


def file_digest(path):
    digest = sha256()
    size = 0
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
            size += len(block)
    return {'name': Path(path).name, 'sha256': digest.hexdigest(), 'bytes': size}


def git_state():
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True, timeout=5).stdout.strip()
        status = subprocess.run(['git', 'status', '--porcelain'], check=True, capture_output=True, text=True, timeout=5).stdout
        return {'commit': head, 'dirty': bool(status.strip())}
    except (OSError, subprocess.SubprocessError):
        return None


def create_manifest(inputs, output, settings=()):
    if not inputs:
        raise ValueError('at least one input file is required')
    output = Path(output)
    if any(Path(path).resolve() == output.resolve() for path in inputs):
        raise ValueError('manifest output must differ from all input files')
    parameters = {}
    for setting in settings:
        key, separator, value = setting.partition('=')
        key, value = key.strip(), value.strip()
        if not separator or not key or not value or key in parameters:
            raise ValueError('settings must have unique non-empty key=value pairs')
        parameters[key] = value
    files = [file_digest(path) for path in inputs]
    if len({entry['name'] for entry in files}) != len(files):
        raise ValueError('input filenames must be distinct')
    try:
        pypdf_version = metadata.version('pypdf')
    except metadata.PackageNotFoundError:
        pypdf_version = None
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(), 'pypdf': pypdf_version, 'git': git_state(), 'settings': parameters, 'inputs': files}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    return manifest
