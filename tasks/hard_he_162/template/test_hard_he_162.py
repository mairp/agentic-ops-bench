from solution import string_to_md5


def test_hidden():
    assert string_to_md5(*['Hello world']) == '3e25960a79dbc69b674cd4ec67a72c62'
    assert string_to_md5(*['']) == None
    assert string_to_md5(*['A B C']) == '0ef78513b0cb8cef12743f5aeb35f888'
    assert string_to_md5(*['password']) == '5f4dcc3b5aa765d61d8327deb882cf99'
    assert string_to_md5(*['5873hajsdklh']) == '0dbb501bb9d84c751d2cf6394d9308c0'
    assert string_to_md5(*['This is a long string to hash to MD5']) == '68b815d9746af477c06423c983860af9'
    assert string_to_md5(*[' \t \n \r \x0c ']) == 'de770a3b085331041645531bd9be7d70'
    assert string_to_md5(*['89704560917293019']) == '6af63c9a5d2e45bff1b65efa69f1a3b5'
    assert string_to_md5(*['abc']) == '900150983cd24fb0d6963f7d28e17f72'
    assert string_to_md5(*['abcd1234']) == 'e19d5cd5af0378da05f63f891c7467af'
    assert string_to_md5(*['John Doe 1234!']) == '878d64322e069bc4d77f3cfbf43e493e'
    assert string_to_md5(*['\n\t   ']) == '0b7d028299b34a3eca02793c59da5e21'
    assert string_to_md5(*['this is a test']) == '54b0c58c7ce9f2a8b551351102ee0938'
    assert string_to_md5(*['test123']) == 'cc03e747a6afbbcbf8be7668acfebee5'
    assert string_to_md5(*['ab']) == '187ef4436122d1cc2f40dc2b92f0eba0'
