from clai.backend.mistral import tools


def test_get_token_length():
    assert tools.get_token_length("Mixing pigments black and white yields grey.") > 0
