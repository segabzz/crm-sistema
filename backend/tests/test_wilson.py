import pytest
from app.services.ranking_service import wilson_score_lower_bound

@pytest.mark.parametrize("positives,total,expected", [
    (0, 0, 0.0),
    (0, 1, 0.0),
    (0, 2, 0.0),
    (1, 1, 0.2065),
    (2, 2, 0.3424),
    (10, 10, 0.7225),
    (100, 100, 0.9630),
    (80, 82, 0.9154),
    (1, 2, 0.0945),
])
def test_wilson_score_known_values(positives, total, expected):
    """Verifica valores analíticos conocidos y calculados en el benchmark."""
    score = wilson_score_lower_bound(positives, total, z=1.96)
    assert score == pytest.approx(expected, abs=1e-4)

def test_wilson_score_penalizes_low_samples():
    """Demuestra que 1 voto positivo de 1 NO supera a 80 votos de 82."""
    score_un_voto = wilson_score_lower_bound(positives=1, total=1)
    score_muchos_votos = wilson_score_lower_bound(positives=80, total=82)
    assert score_un_voto < score_muchos_votos

def test_wilson_score_bounds():
    """El límite inferior siempre debe estar contenido en el intervalo [0.0, 1.0]."""
    for pos, tot in [(0, 5), (3, 10), (10, 10), (50, 100)]:
        score = wilson_score_lower_bound(pos, tot)
        assert 0.0 <= score <= 1.0
