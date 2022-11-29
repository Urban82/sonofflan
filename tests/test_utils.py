from sonofflan.utils import parse_address


def test_parse_address():
    input_data = bytes([1, 2, 3, 4])
    output = parse_address(input_data)
    assert output == "1.2.3.4"
