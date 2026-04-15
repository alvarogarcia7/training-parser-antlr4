"""Tests for Set_.to_dict() method"""
from parser import Set_, Weight


def test_basic_set_to_dict() -> None:
    """Test basic Set_ to_dict conversion"""
    s = Set_(10, Weight(60.0, 'kg'))
    result = s.to_dict(1)

    assert result['setNumber'] == 1
    assert result['repetitions'] == 10
    assert result['weight']['amount'] == 60.0
    assert result['weight']['unit'] == 'kg'
    assert 'rir' not in result


def test_set_with_rir_to_dict() -> None:
    """Test Set_ with RIR to_dict conversion"""
    s = Set_(8, Weight(70.0, 'kg'), rir=2)
    result = s.to_dict(2)

    assert result['setNumber'] == 2
    assert result['repetitions'] == 8
    assert result['weight']['amount'] == 70.0
    assert result['weight']['unit'] == 'kg'
    assert result['rir'] == 2


def test_set_to_dict_with_different_set_numbers() -> None:
    """Test Set_ to_dict with various set numbers"""
    s = Set_(5, Weight(100.0, 'kg'))

    result1 = s.to_dict(1)
    assert result1['setNumber'] == 1

    result5 = s.to_dict(5)
    assert result5['setNumber'] == 5

    result10 = s.to_dict(10)
    assert result10['setNumber'] == 10
