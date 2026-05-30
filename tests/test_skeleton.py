"""
Starter tests for Mutation Shootout.
"""
import pytest
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency
)


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


class TestPipeline:
    def test_happy_flow_eur(self):
        assert compute_total(10, 2) == 25.41

    def test_happy_flow_with_coupon(self):
        ...
