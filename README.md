# Cron Expression Parser

A Python command-line tool that parses and expands cron expressions into their time values.

## What Does This Project Do?

This tool takes a standard cron expression (5 fields: minute, hour, day of month, month, day of week) and expands each field into its complete set of values.

For example, the cron expression `*/15 0 1,15 * 1-5` expands to:
- **minute**: 0, 15, 30, 45 (every 15 minutes)
- **hour**: 0 (midnight)
- **day_of_month**: 1, 15 (1st and 15th of the month)
- **month**: 1-12 (every month)
- **day_of_week**: 1-5 (Monday through Friday)

### Supported Cron Operations

- `*` - All values (e.g., `*` in the hour field = 0-23)
- `*/15` - Every nth value (e.g., `*/15` = 0, 15, 30, 45)
- `1-5` - Range of values (e.g., `1-5` = 1, 2, 3, 4, 5)
- `1,15,30` - List of specific values (e.g., `1,15,30`)
- `5` - Single value (e.g., `5` = only 5)

## Prerequisites

- Python 3.13 or higher (only tested on 3.13.7)
- macOS or Linux operating system

## Installation & Setup

### 1. Clone or Download the Project

cd into the project directory

```bash
cd /path/to/cron-fun
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Cron Parser

With your virtual environment activated, run the parser using Python:

```bash
python src/cron.py -e "*/15 0 1,15 * 1-5"
```

Command line option `-e` or `--expression` is required to provide the cron expression to parse.

### Example

Every 15 minutes, between 12:00 AM and 12:59 AM, on day 1 and 15 of the month, Monday through Friday

```bash
python src/cron.py -e "*/15 0 1,15 * 1-5"
```

Output:
```
minute        0 15 30 45
hour          0
day_of_month  1 15
month         1 2 3 4 5 6 7 8 9 10 11 12
day_of_week   1 2 3 4 5
```

### Error Handling

The tool validates your cron expression and will output error messages when validation fails:

```bash
# Invalid: only 4 fields
python src/cron.py -e "*/10 * 10-20 2,5,12"
# Error: Cron expression must contain 5 fields

# Invalid: value out of range
python src/cron.py -e "60 0 1 1 *"
# Error: For field 'minute' with operation 'single_value', the value must be between 0 and 59
```

## Running Tests

This project uses pytest for testing.
Ensure your virtual environment is activated.

### Run All Tests

```bash
pytest
```

### Run Specific Test Classes

```bash
# Test only cron operation detection
pytest tests/test_cron.py::TestOperationDetection

# Test only value generation
pytest tests/test_cron.py::TestValueGeneration

# Test only field validation
pytest tests/test_cron.py::TestFieldValidation
```

### Run a Specific Test

```bash
pytest tests/test_cron.py::TestCronExpressionProcessing::test_process_cron
```

### A note regarding the tests
The `test_invalid_fields` test could be improved much further by using a `match=""` parameter for the `pytest.raises()` method. For now it only checks that `ValueError` was raised for all tests.
Another improvement could be to create and raise custom exceptions for individual failed field validations.

## Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```
