"""StorageProvider abstract interface."""

from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Abstract file storage provider interface."""

    @abstractmethod
    async def save_file(self, file_content: bytes, destination_path: str) -> str:
        """Saves file binary content and returns the canonical stored file path."""
        pass

    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """Retrieves raw file binary content from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes file from storage."""
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Checks if file exists in storage."""
        pass
