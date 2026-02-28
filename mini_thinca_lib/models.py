from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class TcapPacketType(IntEnum):
    HANDSHAKE = 0x01
    FAREWELL = 0x02
    ERROR = 0x03
    OPERATE_ENTITY = 0x06
    EMPTY_PACKET = 0xFF
    UNKNOWN = 0x00


class TcapRespMessageType(IntEnum):
    OP25 = 0x25
    OP26 = 0x26
    EMPTY_PACKET = 0xFE
    UNKNOWN = 0xFF


@dataclass
class TcapSubPacket:
    subtype: int
    body: bytes = b""
    param: bytes = b"\x00\x00"

    def generate(self) -> bytes:
        op = int(self.subtype).to_bytes(2, "big")
        return bytes([op[0], self.param[0], self.param[1], op[1]]) + len(self.body).to_bytes(2, "big") + self.body


@dataclass
class TcapPacket:
    pkt_type: TcapPacketType
    use_0201: bool = False
    sub_packets: list[TcapSubPacket] = field(default_factory=list)

    def add(self, pkt: TcapSubPacket) -> None:
        self.sub_packets.append(pkt)

    def generate(self) -> bytes:
        body = b"".join(pkt.generate() for pkt in self.sub_packets)
        return bytes([0x02, 0x01 if self.use_0201 else 0x05, int(self.pkt_type)]) + len(body).to_bytes(2, "big") + body


@dataclass
class ParsedMessage:
    msg_type: TcapRespMessageType
    body: bytes


@dataclass
class TcapMessageRequest:
    raw: bytes
    pkt_type: TcapPacketType = TcapPacketType.UNKNOWN
    messages: list[ParsedMessage] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.raw) < 5:
            self.pkt_type = TcapPacketType.EMPTY_PACKET
            return
        self.pkt_type = TcapPacketType(self.raw[2]) if self.raw[2] in [v.value for v in TcapPacketType] else TcapPacketType.UNKNOWN
        content_len = int.from_bytes(self.raw[3:5], "big")
        content = self.raw[5 : 5 + content_len]
        i = 0
        while i + 6 <= len(content):
            op_hi = content[i]
            op_lo = content[i + 3]
            op = (op_hi << 8) | op_lo
            body_len = int.from_bytes(content[i + 4 : i + 6], "big")
            body = content[i + 6 : i + 6 + body_len]
            msg_type = TcapRespMessageType(op) if op in [v.value for v in TcapRespMessageType] else TcapRespMessageType.UNKNOWN
            self.messages.append(ParsedMessage(msg_type=msg_type, body=body))
            i += 6 + body_len


def activation_payload(config: object) -> dict:
    return {
        "certificate": {"ca": ""},
        "endpoints": {
            "terminals": config.terminal_endpoint,
            "statuses": config.statuses_endpoint,
            "sales": config.sales_endpoint,
            "counters": config.counters_endpoint,
        },
    }


def init_setting_payload(config: object, version: str = "10") -> dict:
    return {
        "version": version,
        "supportedBrands": config.available_emoney,
    }
