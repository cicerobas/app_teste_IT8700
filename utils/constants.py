# CONFIG KEYS
TEST_FILES_DIR: str = 'test_files_dir'
SAT_RESOURCE_PATH: str = 'sat_resource_path'
SAT_BAUD_RATE: str = 'sat_baud_rate'
ARDUINO_RESOURCE_PATH: str = 'arduino_resource_path'
ARDUINO_SERIAL_PORT: str = 'arduino_serial_port'
ARDUINO_BAUD_RATE: str = 'arduino_baud_rate'

# CONSTANTS
ARDUINO_READ_TIMEOUT: int = 5
ARDUINO_OUTPUT_PINS: dict[int, str] = {
    4: "CA1",
    5: "CA2",
    6: "CA3",
    7: "CC1",
    8: "CC2",
    9: "CC3",
    10: "Buzzer",
}
STEP_TYPES_MAP: dict[int, str] = {
    1: "Direct Current",
    2: "Current Limiting",
    3: "Automatic Short",
}
AVAILABLE_CHANNELS: list[int] = [1, 3, 4]
