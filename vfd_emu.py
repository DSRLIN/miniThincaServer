from __future__ import annotations

import argparse
import time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", default="COM11")
    args = parser.parse_args()

    try:
        import serial  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("请先安装 pyserial: pip install pyserial") from exc

    with serial.Serial(args.port, baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=None, rtscts=False) as comm:
        comm.dtr = True
        comm.rts = True
        print("vfd online.")
        while True:
            b = comm.read(1)
            if not b or b[0] != 0x1B:
                continue
            cmd = comm.read(1)[0]
            if cmd == 0x0B:
                print("vfd Reset.")
            elif cmd == 0x0C:
                print("vfd Clear.")
            elif cmd == 0x21:
                print(f"vfd PowerOn.{comm.read(1).hex()}")
            elif cmd == 0x30:
                line = comm.read(1)[0]
                size = comm.read(1)[0]
                msg = comm.read(size)
                print(f"vfd Set Message 0x30 Line:{line:02X} {msg.decode('cp932', errors='ignore')}")
            elif cmd == 0x32:
                print(f"vfd Set Language.{comm.read(1).hex()}")
            elif cmd == 0x41:
                print(f"vfd Set Speed:{comm.read(1)[0]}")
            elif cmd == 0x50:
                time.sleep(0.5)
                size = comm.read(1)[0]
                msg = comm.read(size)
                print(f"vfd Set Message 0x50:{msg.decode('cp932', errors='ignore')}")
            else:
                print(f"vfd Unknown cmd:{cmd:02X}")


if __name__ == "__main__":
    main()
