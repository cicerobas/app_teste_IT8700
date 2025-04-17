import tempfile
from datetime import datetime


def generate_report_file(data: dict):
    """Generates a temporary file using [data] values on the test result pattern."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")

    divider = "|" + "=" * 67 + "|\n"
    # Header
    group = data.get("group")
    model = data.get("model")
    customer = data.get("customer")
    sn = data.get("serial_number")
    test_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    tester_id = data.get("tester_id")
    steps = data.get("steps_result")
    lines = []

    # Lines
    channels_line = ""
    static_load_line = ""
    voltage_upper_line = ""
    voltage_lower_line = ""
    power_line = ""
    voltage_output_line = ""
    under_voltage_line = ""
    load_upper_line = ""
    load_lower_line = ""
    load_limit_line = ""
    voltage_ref_line = ""
    shutdown_line = ""
    recovery_line = ""
    short_load_line = ""

    # Write
    temp_file.write(divider)
    temp_file.write("| CEBRA - Power Supply Test Report" + " " * 34 + "|\n")
    temp_file.write(f"| Group: {group + ' ' * (59 - len(group))}|\n")
    temp_file.write(f"| Model: {model + ' ' * (59 - len(model))}|\n")
    temp_file.write(f"| Customer: {customer + ' ' * (56 - len(customer))}|\n")
    temp_file.write(f"| Series Nº: {sn + ' ' * (55 - len(sn))}|\n")
    temp_file.write(f"| Test Date: {test_date + ' ' * (68 - 13 - len(test_date))}|\n")
    temp_file.write(f"| Tested By: {tester_id + ' ' * (68 - 13 - len(tester_id))}|\n")
    for step in steps:
        temp_file.write(divider)
        description = step["description"]
        status = step["step_status"]
        step_type = step["step_type"]
        lines.append(
            f"|-> {description + ' ' * (55 - len(description))}{'[ PASS ]' if status else '[ FAIL ]'} |\n"
        )
        match step_type:
            case 1:
                channels_line = "|" + "=" * 14
                static_load_line = "|Load Current: "
                voltage_upper_line = "|Upper: " + " " * 7
                voltage_lower_line = "|Lower: " + " " * 7
                voltage_output_line = "|Outcome: " + " " * 5
                power_line = "|Power: " + " " * 7
                for channel in step["channels_data"]:
                    static_load = str(channel["load"])
                    voltage_upper = str(channel["upper_voltage"])
                    voltage_lower = str(channel["lower_voltage"])
                    voltage_output = str("%.2f" % channel["outcome_voltage"])
                    power = str("%.2f" % channel["power"])

                    channels_line += f"[Channel {channel['channel_id']}]=="
                    static_load_line += f"[ {static_load + ' ' * (8 - len(static_load))}]A "
                    voltage_upper_line += (
                        f"[ {voltage_upper + ' ' * (8 - len(voltage_upper))}]V "
                    )
                    voltage_lower_line += (
                        f"[ {voltage_lower + ' ' * (8 - len(voltage_lower))}]V "
                    )
                    voltage_output_line += (
                        f"[ {voltage_output + ' ' * (8 - len(voltage_output))}]V "
                    )
                    power_line += f"[ {power + ' ' * (8 - len(power))}]W "
            case 2:
                channels_line = "|" + "=" * 15
                under_voltage_line = "|Under Voltage: "
                load_upper_line = "|Upper: " + " " * 8
                load_lower_line = "|Lower: " + " " * 8
                load_limit_line = "|Outcome: " + " " * 6
                for channel in step["channels_data"]:
                    under_voltage = str(channel["under_voltage"])
                    load_upper = str(channel["load_upper"])
                    load_lower = str(channel["load_lower"])
                    load_limit = str("%.2f" % channel["load"])

                    channels_line += f"[Channel {channel['channel_id']}]=="
                    under_voltage_line += (
                        f"[ {under_voltage + ' ' * (8 - len(under_voltage))}]V "
                    )
                    load_upper_line += f"[ {load_upper + ' ' * (8 - len(load_upper))}]A "
                    load_lower_line += f"[ {load_lower + ' ' * (8 - len(load_lower))}]A "
                    load_limit_line += f"[ {load_limit + ' ' * (8 - len(load_limit))}]A "
            case 3:
                channels_line = "|" + "=" * 15
                voltage_ref_line = "|Voltage Ref. : "
                shutdown_line = "|Shutdown: " + " " * 5
                recovery_line = "|Recovery: " + " " * 5
                short_load_line = "|Load: " + " " * 9
                for channel in step["channels_data"]:
                    voltage_ref = str(channel["voltage_ref"])
                    shutdown = "PASS" if channel["shutdown"] else "FAIL"
                    recovery = "PASS" if channel["recovery"] else "FAIL"
                    load = str(channel["load"])

                    channels_line += f"[Channel {channel['channel_id']}]=="
                    voltage_ref_line += f"[ {voltage_ref + ' ' * (8 - len(voltage_ref))}]V "
                    shutdown_line += f"[ {shutdown + ' ' * (8 - len(shutdown))}]  "
                    recovery_line += f"[ {recovery + ' ' * (8 - len(recovery))}]  "
                    short_load_line += f"[ {load + ' ' * (8 - len(load))}]A "

        lines.append(f"{channels_line + '=' * (68 - len(channels_line))}|\n")
        match step_type:
            case 1:
                lines.append(format_line(static_load_line))
                lines.append(format_line(voltage_upper_line))
                lines.append(format_line(voltage_lower_line))
                lines.append(format_line(voltage_output_line))
                lines.append(format_line(power_line))
            case 2:
                lines.append(format_line(under_voltage_line))
                lines.append(format_line(load_upper_line))
                lines.append(format_line(load_lower_line))
                lines.append(format_line(load_limit_line))
            case 3:
                lines.append(format_line(voltage_ref_line))
                lines.append(format_line(shutdown_line))
                lines.append(format_line(recovery_line))
                lines.append(format_line(short_load_line))

        temp_file.writelines(lines)
        lines.clear()

    temp_file.write(divider)

    temp_file.seek(0)
    temp_file.flush()
    return temp_file


def format_line(text: str) -> str:
    return f"{text + ' ' * (68 - len(text))}|\n"
