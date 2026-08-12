from solution import dict_depth


def test_hidden():
    assert dict_depth(*[{'a': 1, 'b': {'c': {'d': {}}}}]) == 4
    assert dict_depth(*[{'a': 1, 'b': {'c': 'python'}}]) == 2
    assert dict_depth(*[{'1': 'Sun', '2': {'3': {'4': 'Mon'}}}]) == 3
    assert dict_depth(*[{}]) == 1
    assert dict_depth(*[{'a': 1, 'b': {'c': {'d': {'e': {'f': {}}}}}}]) == 6
    assert dict_depth(*[{'1': None, '2': {'3': [1, 2, 3, 'four', {'five': []}]}}]) == 2
    assert dict_depth(*[{'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {'k': {'l': {}}}}}}}}}}}}}]) == 13
    assert dict_depth(*[{'': {'a': {'': {'b': {'': {'c': {'': {'d': {'': {'e': {'': {'f': {}}}}}}}}}}}}}]) == 13
    assert dict_depth(*[{'': {'': {'': {'': {'': {'': {}}}}}}}]) == 7
    assert dict_depth(*[{'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {'k': {'l': {'m': {'n': {'o': {'p': {'q': {}}}}}}}}}}}}}}}}}}]) == 18
    assert dict_depth(*[{'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {'k': {'l': {'m': {'n': {'o': {'p': {'q': {}, 'r': {}}}}}}}}}}}}}}}}}}]) == 18
    assert dict_depth(*[{'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {'k': {'l': {'m': {'n': {'o': {'p': {'q': {'r': {'s': {'t': {'u': {'v': {'w': {'x': {'y': {'z': {}}}}}}}}}}}}}}}}}}}}}}}}}}}]) == 27
    assert dict_depth(*[{'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {}}}}}}}}}}}]) == 11
    assert dict_depth(*[{'a': {'b': {'c': {'d': {}, 'd3': {}}, 'm': {'d': {}, 'd3': {}}}}, 'c': {'b': {'c': {'d': {}, 'd3': {}}, 'm': {'d': {}, 'd3': {}}}}}]) == 5
    assert dict_depth(*[{'': {}, '1': {'FsoqoTrjT': False, 'a': True, 'w': False, 'd3': True, 'qxPg': False, '': True, 'ZUQmkBNwzz': True, 'evQaJAaWcU': False, 'p': True}}]) == 2
