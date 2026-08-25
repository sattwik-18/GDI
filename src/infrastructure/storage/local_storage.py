"""LocalStorageProvider implementation of StorageProvider interface with temp file cleanup."""

import os
import shutil
import aiofiles
import aiofiles.os

from src.domain.interfaces.storage import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Local filesystem implementation of StorageProvider with temp cleanup capabilities."""

    def __init__(self, base_directory: str = "./gdi_storage"):
        self._base_dir = os.path.abspath(base_directory)
        os.makedirs(self._base_dir, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self._base_dir, path)

    async def save_file(self, file_content: bytes, destination_path: str) -> str:
        full_path = self._resolve_path(destination_path)
        dir_name = os.path.dirname(full_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_content)

        return full_path

    async def get_file(self, file_path: str) -> bytes:
        full_path = self._resolve_path(file_path)
        if not await self.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, file_path: str) -> bool:
        full_path = self._resolve_path(file_path)
        if await self.exists(full_path):
            await aiofiles.os.remove(full_path)
            return True
        return False

    async def exists(self, file_path: str) -> bool:
        full_path = self._resolve_path(file_path)
        return await aiofiles.os.path.exists(full_path)

    async def cleanup_temp_files(self, job_id_str: str) -> None:
        """Removes temporary working files for a given job ID to prevent resource leaks."""
        temp_job_dir = os.path.join(self._base_dir, "temp", job_id_str)
        if os.path.exists(temp_job_dir):
            shutil.rmtree(temp_job_dir, ignore_errors=True)
