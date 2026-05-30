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
        ...

    def test_zero_returns_zero(self):
        ...

    @pytest.mark.parametrize("negative", [-1.0, -100])
    def test_negative_raises(self, negative):
        ...


class TestApplyCoupon:
    def test_valid_coupon(self):
        ...

    def test_invalid_coupon(self):
        ...


class TestPipeline:
    def test_happy_flow_eur(self):
        ...

    def test_happy_flow_with_coupon(self):
        ...
