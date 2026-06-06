def is_palindrome(number):
    text = str(number)
    return text == text[::-1]
