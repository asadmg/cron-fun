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


def detect_operation(field: str) -> CRON_OPERATIONS:

    operation = None

    if field.startswith("*") and not field.startswith("*/"):
        operation = "all_items"

    elif field.startswith("*/"):
        operation = "wild_card_with_step_value"

    elif "," in field:
        operation = "list"

    elif "-" in field:
        operation = "range"

    elif field.isdigit():
        operation = "single_value"

    else:
        raise ValueError(f"Invalid operation: {field}")

    return operation


def validate_field(
    cron_part_type: CRON_TIME_PART, operation: CRON_OPERATIONS, value: str | None = None
) -> None:

    if operation == "wild_card_with_step_value":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for wild_card_with_step_value"

        if not (
                int(value) >= MIN_VALUE[cron_part_type]
                and int(value) <= MAX_VALUE[cron_part_type]
        ):
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the value must be between {MIN_VALUE[cron_part_type] + 1} and {MAX_VALUE[cron_part_type]}"
            )

    elif operation == "range":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for range"

        # check if negative value provided
        if value.startswith("-") or value.endswith("-"):
            raise ValueError(
                f"Invalid value provided for field type '{cron_part_type}' with operation '{operation}'"
            )

        lower_bound, upper_bound = map(int, value.split("-"))

        if lower_bound > upper_bound:
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the lower value must be smaller or equal to the upper value"
            )

        if not (
            lower_bound >= MIN_VALUE[cron_part_type]
            and lower_bound <= MAX_VALUE[cron_part_type]
        ):
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the lower value must be between {MIN_VALUE[cron_part_type]} and {MAX_VALUE[cron_part_type]}"
            )

        if not (
            upper_bound >= MIN_VALUE[cron_part_type]
            and upper_bound <= MAX_VALUE[cron_part_type]
        ):
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the upper value must be between {MIN_VALUE[cron_part_type]} and {MAX_VALUE[cron_part_type]}"
            )

    elif operation == "list":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for list"
        values = [
            i
            for i in value.split(",")
            if not (
                int(i) >= MIN_VALUE[cron_part_type]
                and int(i) <= MAX_VALUE[cron_part_type]
            )
        ]
        if values:
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the value must be between {MIN_VALUE[cron_part_type]} and {MAX_VALUE[cron_part_type]}"
            )

    elif operation == "single_value":
        # assert for runtime safety and to satisfy the type checker
        assert value is not None, "value is required for single_value"

        if not (
            int(value) >= MIN_VALUE[cron_part_type]
            and int(value) <= MAX_VALUE[cron_part_type]
        ):
            raise ValueError(
                f"For field type '{cron_part_type}' with operation '{operation}', the value must be between {MIN_VALUE[cron_part_type]} and {MAX_VALUE[cron_part_type]}"
            )


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
        lower_bound, upper_bound = map(int, value.split("-"))
        values = list(range(lower_bound, upper_bound + 1))

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
        raise ValueError("Cron expression must contain 5 fields")

    result: list[str] = []

    for i in range(len(split_cron)):
        part = CRON_PART[i]
        cron_field = split_cron[i]

        operation = detect_operation(cron_field)

        if operation == "all_items":
            val = generate_values(part, operation)

        elif operation == "wild_card_with_step_value":
            validate_field(part, operation, cron_field[2:])
            val = generate_values(part, operation, cron_field[2:])

        else:
            validate_field(part, operation, cron_field)
            val = generate_values(part, operation, cron_field)

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
