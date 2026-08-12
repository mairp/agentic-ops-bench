from solution import numerical_letter_grade


def test_hidden():
    assert numerical_letter_grade(*[[4.0, 3, 1.7, 2, 3.5]]) == ['A+', 'B', 'C-', 'C', 'A-']
    assert numerical_letter_grade(*[[1.2]]) == ['D+']
    assert numerical_letter_grade(*[[0.5]]) == ['D-']
    assert numerical_letter_grade(*[[0.0]]) == ['E']
    assert numerical_letter_grade(*[[1, 0.3, 1.5, 2.8, 3.3]]) == ['D', 'D-', 'C-', 'B', 'B+']
    assert numerical_letter_grade(*[[0, 0.7]]) == ['E', 'D-']
    assert numerical_letter_grade(*[[3.8, 2.5, 3.9, 2.2, 1.0]]) == ['A', 'B-', 'A', 'C+', 'D']
    assert numerical_letter_grade(*[[3.1, 2.7, 1.8, 0.9, 0.5, 4.0]]) == ['B+', 'B-', 'C', 'D', 'D-', 'A+']
    assert numerical_letter_grade(*[[2.2, 1.0, 0.8, 3.5, 0.9, 1.8]]) == ['C+', 'D', 'D', 'A-', 'D', 'C']
    assert numerical_letter_grade(*[[2.7, 1.5, 0.7, 3.3, 3.9]]) == ['B-', 'C-', 'D-', 'B+', 'A']
    assert numerical_letter_grade(*[[3.2, 3.1, 3.0, 2.9, 2.8, 2.7]]) == ['B+', 'B+', 'B', 'B', 'B', 'B-']
    assert numerical_letter_grade(*[[3.3, 2.8, 2.5, 1.9, 1.0]]) == ['B+', 'B', 'B-', 'C', 'D']
    assert numerical_letter_grade(*[[4.0, 4.0, 4.0, 4.0]]) == ['A+', 'A+', 'A+', 'A+']
    assert numerical_letter_grade(*[[1.7, 1.7, 1.7, 1.7]]) == ['C-', 'C-', 'C-', 'C-']
    assert numerical_letter_grade(*[[2.0, 2.0, 2.0, 2.0]]) == ['C', 'C', 'C', 'C']
