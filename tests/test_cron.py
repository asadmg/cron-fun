import pytest
from textwrap import dedent

from src.cron import detect_operation, generate_values, process_cron_expression
from src.cron import CRON_OPERATIONS, CRON_TIME_PART


class TestExceptions:
    def test_invalid_cron_expression(self) -> None:

        invalid_exp = "*/10 * 10-20 2,5,12"

        with pytest.raises(ValueError, match="Cron expression must contain 5 elements"):
            process_cron_expression(invalid_exp)

    def test_invalid_element(self) -> None:

        invalid_element = "xyz"

        with pytest.raises(ValueError, match="Invalid element"):
            detect_operation(invalid_element)


class TestOperationDetection:
    @pytest.mark.parametrize(
        "element, operation",
        [
            ("*", "all_items"),
            ("*/15", "wild_card_with_step_value"),
            ("1,15", "list"),
            ("1-5", "range"),
            ("0", "single_value"),
        ],
    )
    def test_cron_operation_detection(
        self, element: str, operation: CRON_OPERATIONS
    ) -> None:
        result = detect_operation(element)
        assert result == operation


class TestValueGeneration:
    @pytest.mark.parametrize(
        "cron_part, operation, value, expected",
        [
            ("month", "all_items", None, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
            ("minute", "wild_card_with_step_value", 15, [0, 15, 30, 45]),
            ("day_of_week", "range", "1-5", [1, 2, 3, 4, 5]),
            ("day_of_month", "list", "1,15", [1, 15]),
            ("hour", "single_value", "0", [0]),
        ],
    )
    def test_generated_values(
        self,
        cron_part: CRON_TIME_PART,
        operation: CRON_OPERATIONS,
        value: str | None,
        expected: list[int],
    ) -> None:
        result = generate_values(cron_part, operation, value)
        assert result == expected


class TestCronExpressionProcessing:
    @pytest.mark.parametrize(
        "cron_exp, expected",
        [
            (
                "*/15 0 1,15 * 1-5",
                dedent("""
                            minute        0 15 30 45
                            hour          0
                            day_of_month  1 15
                            month         1 2 3 4 5 6 7 8 9 10 11 12
                            day_of_week   1 2 3 4 5
                        """).strip(),
            ),
            (
                "*/10 * 10-20 2,5,12 4-7",
                dedent("""
                            minute        0 10 20 30 40 50
                            hour          0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
                            day_of_month  10 11 12 13 14 15 16 17 18 19 20
                            month         2 5 12
                            day_of_week   4 5 6 7
                        """).strip(),
            ),
        ],
    )
    def test_process_cron(self, cron_exp: str, expected: str) -> None:
        result = process_cron_expression(cron_exp)
        assert result == expected
