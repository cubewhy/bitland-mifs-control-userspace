import enum
import argparse


class WMIMethodType(enum.IntEnum):
    GET = 250
    SET = 251


class WMIMethodName(enum.IntEnum):
    SystemPerMode = 8
    GPUMode = 9
    KeyboardType = 10
    FnLock = 11
    TPLock = 12
    CPUGPUSYSFanSpeed = 13
    RGBKeyboardMode = 16
    RGBKeyboardColor = 17
    RGBKeyboardBrightness = 18
    SystemAcType = 19
    MaxFanSpeedSwitch = 20
    MaxFanSpeed = 21
    CPUThermometer = 22
    CPUPower = 23


class WMISystemPerMode(enum.IntEnum):
    BalanceMode = 0
    PerformanceMode = 1
    QuietMode = 2
    FullspeedMode = 3


class WMIGPUMode(enum.IntEnum):
    HybridMode = 0
    DiscreteMode = 1
    UMAMode = 2


class WMIRGBKeyboardMode(enum.IntEnum):
    OFF = 0
    RGBAutoCyclic = 1
    RGBFixedMode = 2
    CustomColors = 3


class WMIFanType(enum.IntEnum):
    CPUGPUFan = 0
    SYSFan = 1


def build_wmi_buffer(method_type, method_name, data=None):
    """
    Build command
    :param method_type: WMIMethodType (Get/Set)
    :param method_name: WMIMethodName (method)
    :param data: list[int] or int payload
    :return: 32 bytes response
    """
    buffer = [0] * 32
    buffer[1] = int(method_type)
    buffer[3] = int(method_name)

    if data is not None:
        if isinstance(data, list):
            for i, val in enumerate(data):
                if 4 + i < 32:
                    buffer[4 + i] = val
        else:
            buffer[4] = data

    return bytes(buffer)


def get_performance_mode_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.SystemPerMode)


def get_gpu_mode_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.GPUMode)


def get_kbd_led_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.RGBKeyboardBrightness)


def get_kbd_type_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.KeyboardType)


def get_rbg_kbd_color_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.RGBKeyboardColor)


def get_rbg_kbd_mode_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.RGBKeyboardMode)


def get_max_fan_speed_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.MaxFanSpeed)


def get_max_fan_speed_state_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.MaxFanSpeedSwitch)


def get_fan_speeds_cmd():
    return build_wmi_buffer(WMIMethodType.GET, WMIMethodName.CPUGPUSYSFanSpeed)


def set_performance_mode_cmd(mode: WMISystemPerMode):
    return build_wmi_buffer(WMIMethodType.SET, WMIMethodName.SystemPerMode, int(mode))


def set_gpu_mode_cmd(mode: WMIGPUMode):
    return build_wmi_buffer(WMIMethodType.SET, WMIMethodName.GPUMode, int(mode))


def set_kb_brightness_cmd(level: int):
    """level: 0-3"""
    return build_wmi_buffer(
        WMIMethodType.SET, WMIMethodName.RGBKeyboardBrightness, level
    )


def set_kb_color_cmd(r, g, b):
    """Set keyboard color"""
    # change kb mode to FixedMode before set color
    _ = acpi_call(set_kb_mode_cmd(WMIRGBKeyboardMode.RGBFixedMode))
    return build_wmi_buffer(
        WMIMethodType.SET, WMIMethodName.RGBKeyboardColor, [r, g, b]
    )


def set_kb_mode_cmd(mode: WMIRGBKeyboardMode):
    return build_wmi_buffer(WMIMethodType.SET, WMIMethodName.RGBKeyboardMode, int(mode))


def set_fan_max_speed_cmd(fan_type: WMIFanType, speed: int):
    """
    speed: fan speed

    intel_fullspeedMode_FanSpeed_MaxValue = 44
    intel_fullspeedMode_FanSpeed_MinValue = 40
    intel_fastestMode_FanSpeed_MaxValue = 38
    intel_fastestMode_FanSpeed_MinValue = 32
    intel_playingMode_FanSpeed_MaxValue = 35
    intel_playingMode_FanSpeed_MinValue = 26
    intel_workMode_FanSpeed_MaxValue = 29
    intel_workMode_FanSpeed_MinValue = 19

    intel_fullspeedMode_SYSFanSpeed_MaxValue = 82
    intel_fullspeedMode_SYSFanSpeed_MinValue = 75
    intel_fastestMode_SYSFanSpeed_MaxValue = 80
    intel_fastestMode_SYSFanSpeed_MinValue = 70
    intel_playingMode_SYSFanSpeed_MaxValue = 69
    intel_playingMode_SYSFanSpeed_MinValue = 59
    intel_workMode_SYSFanSpeed_MaxValue = 64
    intel_workMode_SYSFanSpeed_MinValue = 25

    amd_fullspeedMode_FanSpeed_MaxValue = 44
    amd_fullspeedMode_FanSpeed_MinValue = 40
    amd_fastestMode_FanSpeed_MaxValue = 38
    amd_fastestMode_FanSpeed_MinValue = 32
    amd_playingMode_FanSpeed_MaxValue = 35
    amd_playingMode_FanSpeed_MinValue = 26
    amd_workMode_FanSpeed_MaxValue = 29
    amd_workMode_FanSpeed_MinValue = 19

    amd_fullspeedMode_SYSFanSpeed_MaxValue = 82
    amd_fullspeedMode_SYSFanSpeed_MinValue = 75
    amd_fastestMode_SYSFanSpeed_MaxValue = 72
    amd_fastestMode_SYSFanSpeed_MinValue = 64
    amd_playingMode_SYSFanSpeed_MaxValue = 69
    amd_playingMode_SYSFanSpeed_MinValue = 59
    amd_workMode_SYSFanSpeed_MaxValue = 64
    amd_workMode_SYSFanSpeed_MinValue = 17

    fullspeedMode_FanSpeed_SaveValue = 43
    fastestMode_FanSpeed_SaveValue = 35
    playingMode_FanSpeed_SaveValue = 29
    workMode_FanSpeed_SaveValue = 22

    fullspeedMode_SYSFanSpeed_SaveValue = 80
    fastestMode_SYSFanSpeed_SaveValue = 69
    playingMode_SYSFanSpeed_SaveValue = 64
    workMode_SYSFanSpeed_SaveValue = 20
    """
    # param1: fan type
    # param2: speed
    return build_wmi_buffer(
        WMIMethodType.SET, WMIMethodName.MaxFanSpeed, [int(fan_type), speed]
    )


def set_fan_switch_cmd(fan_type: WMIFanType, on: bool):
    """Turn the fan maximum speed limit on or off"""
    state = 1 if on else 0
    return build_wmi_buffer(
        WMIMethodType.SET, WMIMethodName.MaxFanSpeedSwitch, [int(fan_type), state]
    )


def acpi_call(buffer_bytes):
    """
    Execute an ACPI call and return the result:
    :param buffer_bytes: A 32-byte bytes object
    """
    # \_SB.PCI0.WMID.WMAA 0 1 b<bytes>
    cmd = f"\\_SB.PCI0.WMID.WMAA 0 1 b{buffer_bytes.hex()}"

    try:
        # write to /proc/acpi/call interface
        with open("/proc/acpi/call", "w") as f:
            f.write(cmd)

        # read response
        with open("/proc/acpi/call", "r") as f:
            result = f.read().strip("\x00").strip()
        return result
    except FileNotFoundError:
        return "Error: acpi_call module not loaded"
    except PermissionError:
        return "Error: Permission denied (run as root)"


def parse_raw_response(resp_str):
    """Parse the string returned by acpi_call into a list of bytes."""
    if not resp_str or "Error" in resp_str:
        return None

    clean_str = resp_str.replace("{", "").replace("}", "").replace("0x", "")
    try:
        if "," in clean_str:
            return [int(x.strip(), 16) for x in clean_str.split(",") if x.strip()]
        else:
            return [int(clean_str, 16)]
    except:
        return None


def get_single_value(data):
    """Parse the single-byte result (data[4])"""
    if data and len(data) >= 5:
        return data[4]
    return 255


def get_fan_speeds(data):
    """
    Analyzes fan speed
    Returns: (CPU speed, GPU speed, SYS speed)
    """
    if not data or len(data) < 12:
        return (-1, -1, -1)

    # (MSB << 8) + LSB
    cpu_fan = (data[5] << 8) + data[4]
    gpu_fan = (data[7] << 8) + data[6]
    sys_fan = (data[11] << 8) + data[10]

    return (cpu_fan, gpu_fan, sys_fan)


def get_rgb_color(data):
    """
    Parse keyboard color
    Returns: (R, G, B)
    """
    if not data or len(data) < 7:
        return (-1, -1, -1)

    return (data[4], data[5], data[6])


def main():
    parser = argparse.ArgumentParser(description="Laptop WMI Control CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Status Command ---
    subparsers.add_parser("status", help="Show current system status (Fans, Mode, RGB)")

    # --- Performance Mode Command ---
    mode_parser = subparsers.add_parser("mode", help="Set system performance mode")
    mode_parser.add_argument(
        "value",
        type=int,
        choices=[0, 1, 2, 3],
        help="0:Balance, 1:Performance, 2:Quiet, 3:Fullspeed",
    )

    # --- GPU Mode Command ---
    gpu_parser = subparsers.add_parser("gpu", help="Set GPU mode")
    gpu_parser.add_argument(
        "value", type=int, choices=[0, 1, 2], help="0:Hybrid, 1:Discrete, 2:UMA"
    )

    # --- Keyboard Command ---
    kb_parser = subparsers.add_parser("kb", help="Keyboard RGB control")
    kb_parser.add_argument(
        "--bright", type=int, choices=[0, 1, 2, 3], help="Set brightness (0-3)"
    )
    kb_parser.add_argument(
        "--mode",
        type=int,
        choices=[0, 1, 2, 3],
        help="Set mode (0:OFF, 1:Cyclic, 2:Fixed, 3:Custom)",
    )
    kb_parser.add_argument(
        "--color",
        type=int,
        nargs=3,
        metavar=("R", "G", "B"),
        help="Set RGB color (e.g., 255 0 0)",
    )

    # --- Fan Command ---
    fan_parser = subparsers.add_parser("fan", help="Fan control")
    fan_parser.add_argument(
        "--type", type=int, choices=[0, 1], default=0, help="0:CPU/GPU Fan, 1:SYS Fan"
    )
    fan_parser.add_argument(
        "--max", type=int, choices=[0, 1], help="Max fan switch (0:OFF, 1:ON)"
    )
    fan_parser.add_argument(
        "--speed", type=int, help="Set max speed value (e.g. 20-80)"
    )

    args = parser.parse_args()

    if args.command == "status":
        # get performance mode
        mode_raw = parse_raw_response(acpi_call(get_performance_mode_cmd()))
        mode_val = get_single_value(mode_raw)

        gpu_mode_raw = parse_raw_response(acpi_call(get_gpu_mode_cmd()))
        gpu_mode_val = get_single_value(gpu_mode_raw)

        # get fan speed
        fan_raw = parse_raw_response(
            acpi_call(
                build_wmi_buffer(WMIMethodType.GET, WMIMethodName.CPUGPUSYSFanSpeed)
            )
        )
        fans = get_fan_speeds(fan_raw)

        temp_raw = parse_raw_response(
            acpi_call(build_wmi_buffer(WMIMethodType.GET, WMIMethodName.CPUThermometer))
        )
        temp = get_single_value(temp_raw)

        print(f"--- System Status ---")
        print(f"Performance Mode: {mode_val} (Refer to WMISystemPerMode)")
        print(f"Temperature:      {temp}°C")
        print(f"GPU Mode:      {gpu_mode_val}")
        print(f"CPU Fan Speed:    {fans[0]} RPM")
        print(f"GPU Fan Speed:    {fans[1]} RPM")
        print(f"SYS Fan Speed:    {fans[2]} RPM")

    elif args.command == "mode":
        res = acpi_call(set_performance_mode_cmd(WMISystemPerMode(args.value)))
        print(f"Set Performance Mode to {args.value}: {res}")

    elif args.command == "gpu":
        res = acpi_call(set_gpu_mode_cmd(WMIGPUMode(args.value)))
        print(f"Set GPU Mode to {args.value}: {res}")

    elif args.command == "kb":
        if args.bright is not None:
            print(f"Set Brightness: {acpi_call(set_kb_brightness_cmd(args.bright))}")
        if args.mode is not None:
            print(
                f"Set KB Mode: {acpi_call(set_kb_mode_cmd(WMIRGBKeyboardMode(args.mode)))}"
            )
        if args.color is not None:
            print(f"Set Color {args.color}: {acpi_call(set_kb_color_cmd(*args.color))}")

    elif args.command == "fan":
        if args.max is not None:
            on = True if args.max == 1 else False
            print(
                f"Set Fan Max Switch: {acpi_call(set_fan_switch_cmd(WMIFanType(args.type), on))}"
            )
        if args.speed is not None:
            print(
                f"Set Fan Max Speed: {acpi_call(set_fan_max_speed_cmd(WMIFanType(args.type), args.speed))}"
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    import os

    if os.getuid() != 0:
        print("Warning: This script usually requires root privileges (sudo).")
    main()
