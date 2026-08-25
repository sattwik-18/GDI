"""Domain repository interfaces."""

from abc import ABC, abstractmethod
import uuid

from src.domain.entities.document import Document
from src.domain.entities.genome import DocumentGenome
from src.domain.entities.processing_job import ProcessingJob


class DocumentRepository(ABC):
    """Repository interface for Document entity persistence."""

    @abstractmethod
    async def save(self, document: Document) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        pass

    @abstractmethod
    async def get_by_hash(self, sha256_hash: str) -> Document | None:
        pass


class JobRepository(ABC):
    """Repository interface for ProcessingJob entity persistence."""

    @abstractmethod
    async def save(self, job: ProcessingJob) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: uuid.UUID) -> ProcessingJob | None:
        pass


class GenomeRepository(ABC):
    """Repository interface for DocumentGenome entity persistence."""

    @abstractmethod
    async def save(self, genome: DocumentGenome) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, genome_id: uuid.UUID) -> DocumentGenome | None:
        pass

    @abstractmethod
    async def get_by_job_id(self, job_id: uuid.UUID) -> DocumentGenome | None:
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: uuid.UUID) -> DocumentGenome | None:
        pass
