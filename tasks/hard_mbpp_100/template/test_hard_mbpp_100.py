from solution import next_smallest_palindrome


def test_hidden():
    assert next_smallest_palindrome(*[99]) == 101
    assert next_smallest_palindrome(*[1221]) == 1331
    assert next_smallest_palindrome(*[120]) == 121
    assert next_smallest_palindrome(*[0]) == 1
    assert next_smallest_palindrome(*[45678]) == 45754
    assert next_smallest_palindrome(*[1]) == 2
    assert next_smallest_palindrome(*[45679]) == 45754
    assert next_smallest_palindrome(*[2]) == 3
    assert next_smallest_palindrome(*[3]) == 4
    assert next_smallest_palindrome(*[45681]) == 45754
    assert next_smallest_palindrome(*[4]) == 5
    assert next_smallest_palindrome(*[5]) == 6
    assert next_smallest_palindrome(*[45683]) == 45754
    assert next_smallest_palindrome(*[45682]) == 45754
    assert next_smallest_palindrome(*[45677]) == 45754
