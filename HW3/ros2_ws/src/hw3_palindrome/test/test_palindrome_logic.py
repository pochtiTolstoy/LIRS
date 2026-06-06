from hw3_palindrome.palindrome_logic import is_palindrome


def test_palindrome_numbers():
    assert is_palindrome(1)
    assert is_palindrome(1221)
    assert is_palindrome(12321)


def test_not_palindrome_numbers():
    assert not is_palindrome(123)
    assert not is_palindrome(100)
