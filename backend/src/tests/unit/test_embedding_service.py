from backend.src.core.embeddings.embedding_service import EmbeddingService


def test_encode_returns_list_of_floats():
    svc = EmbeddingService()
    result = svc.encode("Test text for embedding")
    assert isinstance(result, list)
    assert all(isinstance(v, float) for v in result)
    assert len(result) == 384  # Same dimession from the all-MiniLM-L6-v2


def test_different_texts_produce_different_embeddings():
    svc = EmbeddingService()
    v1 = svc.encode("Login with valid credentials")
    v2 = svc.encode("Transfer funds between accounts")
    assert v1 != v2
