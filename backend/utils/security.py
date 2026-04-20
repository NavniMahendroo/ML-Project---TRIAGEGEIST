import hashlib
import hmac


def hash_password(raw_password: str) -> str:
    """Return a stable SHA-256 hash for password storage/verification."""
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, stored_password: str | None) -> bool:
    if not stored_password:
        return False

    candidate_hash = hash_password(raw_password)

    # Backward compatibility for any accidental plaintext records.
    if hmac.compare_digest(raw_password, stored_password):
        return True

    return hmac.compare_digest(candidate_hash, stored_password)
