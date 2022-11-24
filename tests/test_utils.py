from sonofflan.utils import parse_address

def test_parse_address():
    input = bytes([1, 2, 3, 4])
    output = parse_address(input)
    assert output == "1.2.3.4"