from __future__ import annotations


def reversed_short(value: int) -> bytes:
    return int(value).to_bytes(2, "big", signed=False)


def reversed_int(value: int) -> bytes:
    return int(value).to_bytes(4, "big", signed=False)


def generate_op_cmd_packet(command: str | bytes, op_cmd_packet: bytes | None = None, raw_packet: bool = False) -> bytes:
    command_bytes = command if isinstance(command, bytes) else command.encode("utf-8")
    if op_cmd_packet is None:
        return bytes([len(command_bytes)]) + command_bytes + b"\x00\x00\x00\x00"
    if raw_packet:
        return bytes([len(command_bytes)]) + command_bytes + b"\x00\x00" + reversed_short(len(op_cmd_packet)) + op_cmd_packet
    return (
        bytes([len(command_bytes)])
        + command_bytes
        + b"\x00\x00"
        + reversed_short(len(op_cmd_packet) + 2)
        + reversed_short(len(op_cmd_packet))
        + op_cmd_packet
    )


def to_hex(data: bytes) -> str:
    return data.hex()
