"""Document hash value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentHash:
    """Immutable document hash value object storing SHA-256 and SHA3-256."""

    sha256: str
    sha3_256: str

    def __post_init__(self) -> None:
        if not self.sha256 or len(self.sha256) != 64:
            raise ValueError("Invalid SHA-256 hash length")
        if not self.sha3_256 or len(self.sha3_256) != 64:
            raise ValueError("Invalid SHA3-256 hash length")
