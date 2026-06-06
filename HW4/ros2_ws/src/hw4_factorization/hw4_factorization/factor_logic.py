def factorize(number):
    factors = []
    divisor = 2

    while divisor * divisor <= number:
        while number % divisor == 0:
            factors.append(divisor)
            number = number // divisor
        divisor += 1

    if number > 1:
        factors.append(number)

    return factors
