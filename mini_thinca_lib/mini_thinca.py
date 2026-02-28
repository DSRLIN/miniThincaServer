from __future__ import annotations

import json

from .configuration import Configuration
from .helper import to_hex
from .logger import logger
from .models import activation_payload, init_setting_payload
from .tcap_handler import TcapHandler, TcapRequestType


class MiniThinca:
    def __init__(self, ip_address: str) -> None:
        self.handler = TcapHandler()
        self.config = Configuration(ip_address)

    def dispatch(self, raw_url: str, data: bytes) -> tuple[int, dict[str, str], bytes]:
        out = ""
        out_binary = b""
        use_binary = False
        headers: dict[str, str] = {}

        logger.log("================")
        logger.log(f"Request:{raw_url}")
        if self.config.print_raw_hex:
            logger.log(f"ContentHex:{to_hex(data) if data else ''}")

        parts = [p for p in raw_url.split("/") if p]
        if len(parts) >= 1 and parts[0] == "thinca":
            if len(parts) == 1:
                out = json.dumps(activation_payload(self.config), ensure_ascii=False)
                headers["x-certificate-md5"] = "757cffc53b98fc903476de6a672a1000"
            else:
                route = parts[1]
                if route == "terminals":
                    out = json.dumps(init_setting_payload(self.config, "10"), ensure_ascii=False)
                elif route in {"counters", "statuses", "sales"}:
                    out = ""
                elif route == "common-shop" and len(parts) > 2:
                    method = parts[2]
                    if method == "initauth.jsp":
                        out = f"SERV={self.config.init_auth_endpoint}"
                        headers["Content-Type"] = "application/x-tlam"
                    elif method == "emlist.jsp":
                        out = f"SERV={self.config.em_stage2_endpoint}"
                        headers["Content-Type"] = "application/x-tlam"
                    elif method == "stage2":
                        use_binary = True
                        out_binary = self.handler.handle_tcap_request(TcapRequestType.INIT_AUTH, data)
                        headers["Content-Type"] = "application/x-tcap"
                    elif method == "emstage2":
                        use_binary = True
                        out_binary = self.handler.handle_tcap_request(TcapRequestType.EM_STAGE2, data)
                        headers["Content-Type"] = "application/x-tcap"
                elif route == "emoney" and len(parts) > 4:
                    brand, serial, method = parts[2], parts[3], parts[4]
                    if method in {"tlamAuthorizeSales.jsp", "payment.jsp"}:
                        out = f"SERV={self.config.return_brand_payment_stage2_address(brand, serial)}"
                        headers["Content-Type"] = "application/x-tlam"
                    elif method == "balanceInquiry.jsp":
                        out = f"SERV={self.config.return_brand_payment_stage2_address(brand, serial, 'query_stage2')}"
                        headers["Content-Type"] = "application/x-tlam"
                    elif method == "remove.jsp":
                        out = f"SERV={self.config.return_brand_payment_stage2_address(brand, serial, 'remove_stage2')}"
                        headers["Content-Type"] = "application/x-tlam"
                    elif method == "stage2":
                        use_binary = True
                        out_binary = self.handler.handle_tcap_request(TcapRequestType.AUTHORIZE_SALES, data, brand, serial)
                        headers["Content-Type"] = "application/x-tcap"
                    elif method == "query_stage2":
                        use_binary = True
                        out_binary = self.handler.handle_tcap_request(TcapRequestType.BALANCE_INQUIRE, data, brand, serial)
                        headers["Content-Type"] = "application/x-tcap"
                    elif method == "remove_stage2":
                        use_binary = True
                        out_binary = self.handler.handle_tcap_request(TcapRequestType.REMOVE, data, brand, serial)
                        headers["Content-Type"] = "application/x-tcap"

        if not use_binary:
            out_binary = out.encode("utf-8")

        if self.config.print_raw_hex:
            logger.log(f"Response:{to_hex(out_binary) if out_binary else ''}")
        logger.log("================")
        return 200, headers, out_binary
