import os
from pathlib import Path

import pytest

from app.main import check_model_cache


def test_cache_inscriptible(tmp_path: Path) -> None:
    check_model_cache(str(tmp_path), str(tmp_path / "hf"))
    assert (tmp_path / "hf").is_dir()


@pytest.mark.skipif(os.getuid() == 0, reason="root ecrit partout")
def test_cache_non_inscriptible_echoue_avec_la_cause(tmp_path: Path) -> None:
    tmp_path.chmod(0o500)
    try:
        with pytest.raises(RuntimeError, match="ECARTS"):
            check_model_cache(str(tmp_path))
    finally:
        tmp_path.chmod(0o700)


def test_lifespan_verifie_les_caches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Demarrage complet (lifespan) avec des caches inscriptibles."""
    from fastapi.testclient import TestClient

    from app.core.config import get_settings
    from app.main import app

    monkeypatch.setenv("ML_MODEL_CACHE", str(tmp_path / "models"))
    monkeypatch.setenv("HF_HOME", str(tmp_path / "models" / "hf"))
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            assert client.get("/health").status_code == 200
        assert (tmp_path / "models" / "hf").is_dir()
    finally:
        get_settings.cache_clear()
