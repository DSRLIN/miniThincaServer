from __future__ import annotations

from enum import IntEnum


class ThincaBrandType(IntEnum):
    NANACO = 1
    EDY = 2
    ID = 3
    QUICPAY = 4
    TRANSPORT = 5
    WAON = 6
    NANACO2 = 7
    PASELI = 8
    SAPICA = 9


class Configuration:
    def __init__(self, ip_address: str) -> None:
        self._ip_address = ip_address
        self.print_raw_hex = False
        self._brand_switch = {
            ThincaBrandType.NANACO: True,
            ThincaBrandType.EDY: False,
            ThincaBrandType.ID: False,
            ThincaBrandType.QUICPAY: False,
            ThincaBrandType.TRANSPORT: True,
            ThincaBrandType.WAON: True,
            ThincaBrandType.NANACO2: False,
            ThincaBrandType.PASELI: True,
            ThincaBrandType.SAPICA: False,
        }

    @property
    def terminal_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/terminals"

    @property
    def statuses_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/statuses"

    @property
    def sales_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/sales"

    @property
    def counters_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/counters"

    @property
    def init_auth_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/common-shop/stage2"

    @property
    def em_stage2_endpoint(self) -> str:
        return f"http://{self._ip_address}/thinca/common-shop/emstage2"

    @property
    def available_emoney(self) -> list[int]:
        return [int(k) for k, v in self._brand_switch.items() if v]

    @property
    def available_emoney_result_code(self) -> list[int]:
        return [1 for _, v in self._brand_switch.items() if v]

    def return_brand_payment_stage2_address(self, brand_name: str, term_serial: str, stage2: str = "stage2") -> str:
        return f"http://{self._ip_address}/thinca/emoney/{brand_name}/{term_serial}/{stage2}"

    def return_brand_url(self, term_serial: str) -> list[str]:
        out: list[str] = []
        for k, v in self._brand_switch.items():
            if not v:
                continue
            out.append(f"http://{self._ip_address}/thinca/emoney/{k.name.lower()}/{term_serial}/")
        return out
