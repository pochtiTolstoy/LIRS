from hw4_factorization.factor_logic import factorize


def test_factorize_composite_number():
    assert factorize(84) == [2, 2, 3, 7]


def test_factorize_prime_number():
    assert factorize(13) == [13]


def test_factorize_one():
    assert factorize(1) == []
