"""
Starter tests for Mutation Shootout.
"""
import pytest
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency, compute_bulk_total
)
from billing.calculator import (
    _round, bulk_discount, compute_refund, parse_iso_date, split_payment,
    tax_breakdown, validate_coupon, validate_tax_number
)


class TestRound:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, 0),
            (-1, -1),
            (-1.544, -1.54),
            (1, 1),
            (1.1, 1.1),
            (1.9, 1.9),
            (1.5, 1.5),
            (1.544, 1.54),
            (1.55, 1.55),
            (1.555, 1.56),
            (1 / 3, 0.33),
        ],
        ids=lambda case: str(case),
    )
    def test_round(self, value, expected):
        assert _round(value) == expected


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


class TestSplitPayment:
    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "even split",
                "total": 10,
                "parts": 2,
                "expected": [5, 5],
            },
            {
                "name": "rounding diff goes to last part",
                "total": 10,
                "parts": 3,
                "expected": [3.33, 3.33, 3.34],
            },
            {
                "name": "negative parts",
                "total": 10,
                "parts": -1,
                "error_match": "parts must be > 0",
            },
            {
                "name": "zero parts",
                "total": 10,
                "parts": 0,
                "error_match": "parts must be > 0",
            },
        ],
        ids=lambda case: case["name"],
    )
    def test_split_payment(self, case):
        error_match = case.get("error_match")

        if error_match is not None:
            with pytest.raises(ValueError, match=error_match):
                split_payment(case["total"], case["parts"])
            return

        assert split_payment(case["total"], case["parts"]) == case["expected"]


class TestConvertCurrency:
    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "eur to eur",
                "amount_eur": 10,
                "to": "EUR",
                "expected": 10,
            },
            {
                "name": "eur to usd",
                "amount_eur": 10,
                "to": "USD",
                "expected": 10.87,
            },
            {
                "name": "lowercase currency",
                "amount_eur": 10,
                "to": "usd",
                "expected": 10.87,
            },
            {
                "name": "unsupported currency",
                "amount_eur": 10,
                "to": "JPY",
                "error_match": "Unsupported currency JPY",
            },
        ],
        ids=lambda case: case["name"],
    )
    def test_convert_currency(self, case):
        error_match = case.get("error_match")

        if error_match is not None:
            with pytest.raises(KeyError, match=error_match):
                convert_currency(case["amount_eur"], case["to"])
            return

        assert convert_currency(case["amount_eur"], case["to"]) == case["expected"]


class TestParseIsoDate:
    @pytest.mark.parametrize(
        ("date_str", "expected", "error", "error_match"),
        [
            ("2026-05-30", "2026-05-30 00:00:00", None, None),
            ("2026-05-30T14:15:16", "2026-05-30 14:15:16", None, None),
            ("2026-05-30T14:15:16+03:00", "2026-05-30 14:15:16+03:00", None, None),
            ("not-a-date", None, ValueError, "Invalid isoformat string: 'not-a-date'"),
            (None, None, TypeError, "fromisoformat: argument must be str"),
        ],
        ids=lambda case: str(case),
    )
    def test_parse_iso_date(self, date_str, expected, error, error_match):
        if error_match is not None:
            with pytest.raises(error, match=error_match):
                parse_iso_date(date_str)
            return

        assert str(parse_iso_date(date_str)) == expected


class TestComputeRefund:
    @pytest.mark.parametrize(
        "case",
        [
            {
                "name": "percent=-0.1",
                "total_paid": 10,
                "percentage": -0.1,
                "error_match": "percentage 0..1",
            },
            {
                "name": "percent=1.1",
                "total_paid": 10,
                "percentage": 1.1,
                "error_match": "percentage 0..1",
            },
            {
                "name": "percent=0",
                "total_paid": 10,
                "percentage": 0,
                "expected": 0,
            },
            {
                "name": "percent=0.5",
                "total_paid": 10,
                "percentage": 0.5,
                "expected": 5,
            },
            {
                "name": "percent=1",
                "total_paid": 10,
                "percentage": 1,
                "expected": 10,
            },
            { # suspicious
                "name": "total_paid=0",
                "total_paid": 0,
                "percentage": 0.5,
                "expected": 0,
            },
            { # suspicious
                "name": "total_paid=-10",
                "total_paid": -10,
                "percentage": 0.5,
                "expected": -5,
            },
        ],
        ids=lambda case: case["name"],
    )
    def test_compute_refund(self, case):
        error_match = case.get("error_match")

        if error_match is not None:
            with pytest.raises(ValueError, match=error_match):
                compute_refund(case["total_paid"], case["percentage"])
            return

        assert compute_refund(case["total_paid"], case["percentage"]) == case["expected"]


class TestBulkDiscount:
    @pytest.mark.parametrize(
        ("qty", "expected"),
        [
            (-1, 0),
            (0, 0),
            (1, 0),
            (9, 0),
            (10, 0.08),
            (19, 0.08),
            (20, 0.15),
            (21, 0.15),
        ],
        ids=lambda case: str(case),
    )
    def test_bulk_discount(self, qty, expected):
        assert bulk_discount(qty) == expected


class TestComputeBulkTotal:
    @pytest.mark.parametrize(
        ("unit_price", "qty", "expected", "error_match"),
        [
            (10, 0, None, "qty must be positive"),
            (10, -1, None, "qty must be positive"),
            (-10, 1, None, "net must be non‑negative"),
            (0, 1, 0, None),
            (10.5, 1, 12.71, None),
            (10, 9, 108.9, None),
            (10, 10, 111.32, None),
            (10, 20, 205.7, None),
        ],
        ids=lambda case: str(case),
    )
    def test_compute_bulk_total(self, unit_price, qty, expected, error_match):
        if error_match is not None:
            with pytest.raises(ValueError, match=error_match):
                compute_bulk_total(unit_price, qty)
            return

        assert compute_bulk_total(unit_price, qty) == expected


class TestTaxBreakdown:
    @pytest.mark.parametrize(
        ("net", "expected"),
        [
            (0, (0, 0)),
            (10, (10, 2.1)),
            (10.5, (10.5, 2.21)),
            (-10, (-10, -2.1)), # suspicious
        ],
        ids=lambda case: str(case),
    )
    def test_tax_breakdown(self, net, expected):
        assert tax_breakdown(net) == expected


class TestValidateTaxNumber:
    @pytest.mark.parametrize(
        ("tax_num", "expected", "error_match"),
        [
            ("LV1234567890", True, None),
            ("LV123456789", False, None),
            ("LV12345678901", False, None),
            ("EE1234567890", False, None),
            ("", False, None),
            (None, None, "'NoneType' object has no attribute 'startswith'"),
        ],
        ids=lambda case: str(case),
    )
    def test_validate_tax_number(self, tax_num, expected, error_match):
        if error_match is not None:
            with pytest.raises(AttributeError, match=error_match):
                validate_tax_number(tax_num)
            return

        assert validate_tax_number(tax_num) is expected
