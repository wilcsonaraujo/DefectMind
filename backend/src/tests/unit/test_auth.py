from backend.src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestHashPassword:
    def test_hash_returns_bcrypt_format(self):
        hashed = hash_password("MinhaSenh@123")
        assert hashed.startswith("$2b$")

    def test_different_hashes_for_same_password(self):
        """bccrypt should generate different hashes for the same password due to salting."""
        h1 = hash_password("MinhaSenh@123")
        h2 = hash_password("MinhaSenh@123")
        assert h1 != h2


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        hashed = hash_password("MinhaSenh@123")
        assert verify_password("MinhaSenh@123", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("MinhaSenh@123")
        assert verify_password("WrongPassword", hashed) is False

    def test_invalid_hash_returns_false(self):
        """Invalid hash should not raise an exception — it should return False."""
        assert verify_password("any", "hash_invalido") is False


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token("user-id-123", "admin")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-id-123"
        assert payload["role"] == "admin"

    def test_token_has_expiration(self):
        token = create_access_token("user-id-123", "viewer")
        payload = decode_access_token(token)
        assert "exp" in payload
