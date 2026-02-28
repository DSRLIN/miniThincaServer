from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .builder import Builder
from .logger import logger
from .models import TcapMessageRequest, TcapPacketType


class TcapRequestType(str, Enum):
    INIT_AUTH = "initAuth"
    EM_STAGE2 = "emStage2"
    AUTHORIZE_SALES = "AuthorizeSales"
    BALANCE_INQUIRE = "BalanceInquire"
    REMOVE = "Remove"
    OTHERS = "Others"


@dataclass
class MachineInfo:
    req_type: TcapRequestType
    state: str
    first_request: datetime
    last_request: datetime


class TcapHandler:
    def __init__(self) -> None:
        self.machine_info: dict[str, MachineInfo] = {}

    def handle_tcap_request(self, request_method: TcapRequestType, payload: bytes, brand_name: str = "", term_serial: str = "") -> bytes:
        req = TcapMessageRequest(payload)
        logger.log(f"Packet Type:{req.pkt_type}")
        for m in req.messages:
            logger.log(f"Message Type:{m.msg_type}")

        if req.pkt_type == TcapPacketType.HANDSHAKE:
            return Builder.build_handshake_result()
        if req.pkt_type == TcapPacketType.EMPTY_PACKET:
            if request_method in [TcapRequestType.INIT_AUTH, TcapRequestType.EM_STAGE2, TcapRequestType.REMOVE]:
                return Builder.build_get_machine_info_packet()
            if request_method in [TcapRequestType.AUTHORIZE_SALES, TcapRequestType.BALANCE_INQUIRE]:
                if term_serial:
                    self.machine_info[f"{term_serial}:{request_method}"] = MachineInfo(
                        req_type=request_method,
                        state="RequestOp_InitCardSwipe",
                        first_request=datetime.now(),
                        last_request=datetime.now(),
                    )
                return Builder.build_get_aime_card_result(brand_type=8, message_id=30, timeout=5000)
            return Builder.build_farewell_result()

        if req.pkt_type == TcapPacketType.OPERATE_ENTITY:
            if request_method in [TcapRequestType.INIT_AUTH, TcapRequestType.EM_STAGE2]:
                return self._handle_init_auth_packet(req, em_stage2=request_method == TcapRequestType.EM_STAGE2)
            if request_method == TcapRequestType.REMOVE:
                return Builder.build_farewell_result()
            if request_method == TcapRequestType.AUTHORIZE_SALES:
                return self._handle_auth_sales_packet(term_serial)
            if request_method == TcapRequestType.BALANCE_INQUIRE:
                return self._handle_balance_inquire_packet(term_serial)

        return Builder.build_farewell_result()

    def _handle_auth_sales_packet(self, term_serial: str) -> bytes:
        key = f"{term_serial}:{TcapRequestType.AUTHORIZE_SALES}"
        if key not in self.machine_info:
            return Builder.build_farewell_result()
        self.machine_info.pop(key, None)
        return Builder.build_success_payment_result(brand_type=8)

    def _handle_balance_inquire_packet(self, term_serial: str) -> bytes:
        key = f"{term_serial}:{TcapRequestType.BALANCE_INQUIRE}"
        if key not in self.machine_info:
            return Builder.build_farewell_result()
        self.machine_info.pop(key, None)
        return Builder.build_success_payment_result(brand_type=8, amount=0)

    def _extract_serial(self, req: TcapMessageRequest, em_stage2: bool = False) -> str:
        for message in req.messages:
            if len(message.body) <= 6:
                continue
            try:
                obj = json.loads(message.body[6:].decode("utf-8", errors="ignore"))
            except json.JSONDecodeError:
                continue
            key = "TermSerial" if em_stage2 else "UniqueCode"
            serial = obj.get(key) or obj.get("AdditionalSecurityInformation", {}).get(key)
            if serial:
                return serial
        return ""

    def _handle_init_auth_packet(self, req: TcapMessageRequest, em_stage2: bool = False) -> bytes:
        serial = self._extract_serial(req, em_stage2=em_stage2)
        if not serial:
            return Builder.build_get_machine_info_packet()
        if em_stage2:
            return Builder.build_init_auth_operate_msg_result_em2(serial)
        return Builder.build_init_auth_operate_msg_result()
