from typing import Literal

type CRON_OPERATIONS = Literal[
    "all_items", "wild_card_with_step_value", "range", "list", "single_value"
]

type CRON_TIME_PART = Literal["minute", "hour", "day_of_month", "month", "day_of_week"]

MIN_VALUE: dict[CRON_TIME_PART, int] = {
    "minute": 0,
    "hour": 0,
    "day_of_month": 1,
    "month": 1,
    "day_of_week": 1,
}

MAX_VALUE: dict[CRON_TIME_PART, int] = {
    "minute": 59,
    "hour": 23,
    "day_of_month": 31,
    "month": 12,
    "day_of_week": 7,
}

CRON_PART: dict[int, CRON_TIME_PART] = {
    0: "minute",
    1: "hour",
    2: "day_of_month",
    3: "month",
    4: "day_of_week",
}


def detect_operation(element: str) -> CRON_OPERATIONS:

    operation = None

    if element.startswith("*") and not element.startswith("*/"):
        operation = "all_items"

    elif element.startswith("*/"):
        operation = "wild_card_with_step_value"

    elif "," in element:
        operation = "list"

    elif "-" in element:
        operation = "range"

    elif element.isdigit():
        operation = "single_value"

    else:
        raise ValueError(f"Invalid element: {element}")

    return operation


def generate_values(
    cron_part_type: CRON_TIME_PART, operation: CRON_OPERATIONS, value: str | None = None
) -> list[int]:

    if operation == "all_items":
        values = list(range(MIN_VALUE[cron_part_type], MAX_VALUE[cron_part_type] + 1))

    elif operation == "wild_card_with_step_value":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for wild_card_with_step_value"
        values = list(
            range(MIN_VALUE[cron_part_type], MAX_VALUE[cron_part_type] + 1, int(value))
        )

    elif operation == "range":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for range"
        lower_bound, upper_bound = value.split("-")
        values = list(range(int(lower_bound), int(upper_bound) + 1))

    elif operation == "list":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for list"
        values = [int(i) for i in value.split(",")]

    elif operation == "single_value":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for single_value"
        values = [int(value)]

    return values


def process_cron_expression(expression: str) -> str:

    split_cron = expression.split()

    if len(split_cron) != 5:
        raise ValueError("Cron expression must contain 5 elements")

    result: list[str] = []

    for i in range(len(split_cron)):
        part = CRON_PART[i]
        cron_element = split_cron[i]

        operation = detect_operation(cron_element)

        if operation == "all_items":
            val = generate_values(part, operation)

        elif operation == "wild_card_with_step_value":
            val = generate_values(part, operation, cron_element[2:])

        else:
            val = generate_values(part, operation, cron_element)

        result.append(f"{part:<14}{' '.join(map(str, val))}")

    return "\n".join(result)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse cron expression")
    parser.add_argument(
        "-e",
        "--expression",
        type=str,
        required=True,
        help="cron expression to be parsed",
    )

    args = parser.parse_args()

    parsed_exp = process_cron_expression(args.expression)

    print(parsed_exp)
