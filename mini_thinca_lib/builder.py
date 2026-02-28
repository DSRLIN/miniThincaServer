from __future__ import annotations

import json

from .helper import generate_op_cmd_packet
from .models import TcapPacket, TcapPacketType, TcapSubPacket


class Builder:
    @staticmethod
    def build_handshake_result() -> bytes:
        p = TcapPacket(TcapPacketType.HANDSHAKE)
        p.add(TcapSubPacket(0x23))
        p.add(TcapSubPacket(0x81, b"\x02\x05\x00"))
        p.add(TcapSubPacket(0x24))
        return p.generate()

    @staticmethod
    def build_farewell_result() -> bytes:
        p = TcapPacket(TcapPacketType.FAREWELL)
        p.add(TcapSubPacket(0x23))
        p.add(TcapSubPacket(0x25, b"\x12\x34\x56\x78"))
        p.add(TcapSubPacket(0x24))
        return p.generate()

    @staticmethod
    def build_get_machine_info_packet() -> bytes:
        p = TcapPacket(TcapPacketType.OPERATE_ENTITY)
        cmd = generate_op_cmd_packet("REQUEST")
        sub = TcapSubPacket(0x25, cmd)
        sub.param = b"\x00\x01"
        p.add(sub)
        return p.generate()

    @staticmethod
    def build_get_aime_card_result(brand_type: int, message_id: int, timeout: int = 5000) -> bytes:
        p = TcapPacket(TcapPacketType.OPERATE_ENTITY)
        msg = json.dumps({"brandType": brand_type, "messageId": message_id, "timeout": timeout}).encode()
        s1 = TcapSubPacket(0x25, generate_op_cmd_packet("STATUS", b"\x00" * 8 + msg))
        s1.param = b"\x00\x03"
        p.add(s1)
        s2 = TcapSubPacket(0x25, generate_op_cmd_packet("OPEN_RW", b"\x00\x00\x09", raw_packet=True))
        s2.param = b"\x00\x08"
        p.add(s2)
        return p.generate()

    @staticmethod
    def build_success_payment_result(brand_type: int, amount: int = 100, card_no: str = "01391144551419198100", seq_number: str = "1") -> bytes:
        p = TcapPacket(TcapPacketType.OPERATE_ENTITY)
        payload = json.dumps(
            {"serviceName": "AuthorizeSales", "brandType": brand_type, "amount": amount, "cardNo": card_no, "seq": seq_number}
        ).encode()
        s = TcapSubPacket(0x26, b"\x00\x00\x00\x00\x00\x00" + payload)
        p.add(s)
        return p.generate()

    @staticmethod
    def build_init_auth_operate_msg_result_em2(serial: str) -> bytes:
        p = TcapPacket(TcapPacketType.OPERATE_ENTITY)
        payload = json.dumps({"TermSerial": serial}).encode()
        p.add(TcapSubPacket(0x26, b"\x00\x00\x00\x00\x00\x00" + payload))
        return p.generate()

    @staticmethod
    def build_init_auth_operate_msg_result() -> bytes:
        p = TcapPacket(TcapPacketType.OPERATE_ENTITY)
        p.add(TcapSubPacket(0x26, b"\x00\x00\x00\x00\x00\x00{}"))
        return p.generate()
