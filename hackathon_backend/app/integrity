import hashlib
from typing import Union


def calculate_sha256(data: Union[bytes, str]) -> str:
    """
    Calculate the SHA-256 hash of evidence data.

    - bytes are used directly
    - strings are encoded as UTF-8
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    return hashlib.sha256(data).hexdigest()
