import pytest
from services.validation_service import ValidationService

def test_t4_charge_boundary_values():
    """
    Test T4 / BR4:
    If chargeable amount is below Rs.1000: charge = Rs.50
    If amount is Rs.1000 or above: charge = Rs.0
    If scenario is not chargeable / zero: charge = Rs.0

    Important boundary tests:
    Rs.999  -> Rs.50
    Rs.1000 -> Rs.0
    Rs.1001 -> Rs.0
    """
    # Boundary 1: Rs. 999 -> Rs. 50
    assert ValidationService.calculate_charge(999) == 50.0
    assert ValidationService.calculate_charge("999") == 50.0
    assert ValidationService.calculate_charge(999.99) == 50.0

    # Boundary 2: Rs. 1000 -> Rs. 0
    assert ValidationService.calculate_charge(1000) == 0.0
    assert ValidationService.calculate_charge("1000") == 0.0
    assert ValidationService.calculate_charge(1000.0) == 0.0

    # Boundary 3: Rs. 1001 -> Rs. 0
    assert ValidationService.calculate_charge(1001) == 0.0
    assert ValidationService.calculate_charge("1001") == 0.0
    assert ValidationService.calculate_charge(2500.0) == 0.0

    # Intermediate small amounts below 1000
    assert ValidationService.calculate_charge(0.0) == 50.0
    assert ValidationService.calculate_charge(100) == 50.0

    # None / Unchargeable scenario
    assert ValidationService.calculate_charge(None) == 0.0
    assert ValidationService.calculate_charge(-50) == 0.0
