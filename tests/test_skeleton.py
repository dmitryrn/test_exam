"""
Starter tests for Mutation Shootout.
"""
import pytest
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency
)
from billing.calculator import validate_coupon


class TestPriceWithTax:
    def test_positive_value(self):
        assert price_with_tax(10) == 12.1

    def test_zero_returns_zero(self):
        assert price_with_tax(0) == 0

    @pytest.mark.parametrize("negative", [-1.0, -100])
    def test_negative_raises(self, negative):
        with pytest.raises(ValueError, match="net must be non‑negative"):
            price_with_tax(negative)


class TestApplyCoupon:
    def test_valid_coupon(self):
        assert apply_coupon(100, "SPORT10") == 90
        assert apply_coupon(100, "sport10") == 90
        assert apply_coupon(100, "spoRt10") == 90

    def test_invalid_coupon(self):
        assert apply_coupon(100, "INVALID") == 100
        assert apply_coupon(100, "SPORT1") == 100


class TestComputeSubtotal:
    def test_happy_path(self):
        assert compute_subtotal(10, 2) == 20
        assert compute_subtotal(2.6, 2) == 5.2

    @pytest.mark.parametrize("qty", [-1, 0])
    def test_invalid_values(self, qty):
        with pytest.raises(ValueError, match="qty must be positive"):
            compute_subtotal(10, qty)


class TestBookingFee:
    def test_happy_path(self):
        assert booking_fee(2) == 1

    # suspicious
    def test_zero_and_negative_values(self):
        assert booking_fee(0) == 0
        assert booking_fee(-1) == -0.5
        assert booking_fee(-100) == -50


class TestPipeline:
    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "without coupon",
                "unit_price": 10,
                "qty": 2,
                "expected": 25.41,
            },
            {
                "name": "with coupon",
                "unit_price": 10,
                "qty": 2,
                "coupon": "SPORT10",
                "expected": 22.87,
            },
            {
                "name": "invalid coupon does not apply",
                "unit_price": 10,
                "qty": 2,
                "coupon": "NON_EXISTING",
                "expected": 25.41,
            },
            {
                "name": "negative unit price",
                "unit_price": -10,
                "qty": 2,
                "error_match": "net must be non‑negative",
            },
            {
                "name": "negative qty",
                "unit_price": 10,
                "qty": -1,
                "error_match": "qty must be positive",
            },
            {
                "name": "zero qty",
                "unit_price": 10,
                "qty": 0,
                "error_match": "qty must be positive",
            },
        ],
        ids=lambda case: case["name"],
    )
    def test_happy_flow_eur(self, case):
        error_match = case.get("error_match")

        if error_match is not None:
            with pytest.raises(ValueError, match=error_match):
                compute_total(case["unit_price"], case["qty"], case.get("coupon"))
            return

        assert compute_total(case["unit_price"], case["qty"], case.get("coupon")) == case.get("expected")


class TestValidateCoupon:
    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "valid coupon",
                "coupon": "SPORT10",
                "expected": True,
            },
            {
                "name": "lowercase valid coupon",
                "coupon": "sport10",
                "expected": True,
            },
            {
                "name": "non existing coupon",
                "coupon": "NON_EXISTING",
                "expected": False,
            },
            {
                "name": "similar invalid coupon",
                "coupon": "SPORT1",
                "expected": False,
            },
            {
                "name": "empty string input",
                "coupon": "",
                "expected": False,
            },
            {
                "name": "none input",
                "coupon": None,
                "error_match": "'NoneType' object has no attribute 'upper'",
            },
        ],
        ids=lambda case: case["name"],
    )
    def test_validate_coupon(self, case):
        error_match = case.get("error_match")

        if error_match is not None:
            with pytest.raises(AttributeError, match=error_match):
                validate_coupon(case["coupon"])
            return

        assert validate_coupon(case["coupon"]) is case["expected"]
