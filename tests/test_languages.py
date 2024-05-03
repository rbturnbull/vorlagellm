from vorlagellm.languages import convert_language_code

def test_arabic():
    assert convert_language_code("ara") == "Arabic"
    assert convert_language_code("arabic") == "arabic"


def test_greek():
    assert convert_language_code("grc") == "Ancient Greek"
    assert convert_language_code("gre") == "Modern Greek"
    assert convert_language_code("ell") == "Modern Greek"
    assert convert_language_code("greek") == "greek"