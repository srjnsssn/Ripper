import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_KEY_PATH = Path(__file__).resolve().parent.parent.parent / ".vault.key"


class Vault:
    _instance: "Vault | None" = None
    _key: bytes | None = None

    def __new__(cls) -> "Vault":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def is_initialized(self) -> bool:
        return self._key is not None

    def initialize(self) -> None:
        if not VAULT_KEY_PATH.exists():
            key = AESGCM.generate_key(bit_length=256)
            VAULT_KEY_PATH.write_bytes(key)
            VAULT_KEY_PATH.chmod(0o600)
            self._key = key
        else:
            self._key = VAULT_KEY_PATH.read_bytes()

    def encrypt(self, plaintext: str) -> tuple[bytes, bytes, bytes]:
        if self._key is None:
            raise RuntimeError("Vault not initialized. Call vault.initialize() first.")
        aesgcm = AESGCM(self._key)
        iv = os.urandom(12)
        ct_with_tag = aesgcm.encrypt(iv, plaintext.encode(), None)
        ciphertext = ct_with_tag[:-16]
        tag = ct_with_tag[-16:]
        return ciphertext, iv, tag

    def decrypt(self, ciphertext: bytes, iv: bytes, tag: bytes) -> str:
        if self._key is None:
            raise RuntimeError("Vault not initialized. Call vault.initialize() first.")
        aesgcm = AESGCM(self._key)
        ct_with_tag = ciphertext + tag
        plaintext = aesgcm.decrypt(iv, ct_with_tag, None)
        return plaintext.decode()


vault = Vault()
