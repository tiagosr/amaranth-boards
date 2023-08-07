import os
import subprocess

from amaranth.build import Resource, Subsignal, Pins, Clock, Attrs, Connector
from amaranth.vendor.intel import IntelPlatform
from .resources import *


__all__ = [ "MAX1000Platform", "MAX1000Platform_32M" ]


class MAX1000Platform(IntelPlatform):
    device = "10M08SA"
    package = "U169"
    speed = "C8G"

    resources = [
        Resource("clk12", 0, Pins("H6", dir="i"), Clock(12e6),
                 Attrs(io_standard="3.3-V LVCMOS")),
        
        *LEDResources(
            pins="A8 A9 A11 A10 B10 C9 C10 D8",
            attrs=Attrs(io_standard="3.3-V LVCMOS")
        ),
        *ButtonResources(
            pins="E6", invert=True,
            attrs=Attrs(io_standard="3.3 V Schmitt Trigger")
        ),

        SDRAMResource(0,
            clk="M9", cke="M8", cs_n="M4", we_n="K7", ras_n="M7", cas_n="N7",
            ba="N6 K8", a="K6 M5 N5 J8 N10 M11 N9 L10 M13 N8 N4 M10 L11 M12",
            dq="D11 G10 F10 F9 E10 D9 G9 F8 F13 E12 D12 C12 B12 B13 A12",
            dqm="E9 F12", attrs=Attrs(io_standard="3.3-V LVCMOS")
        ),

        *SPIFlashResources(0,
            cs_n="B3", clk="A3", copi="A2", cipo="B2", hold_n="C4", conn="B9",
            attrs=Attrs(io_standard="3.3-V LVCMOS")
        ),

        Resource("accelerometer_lis3dh", 0,
            Subsignal("int", Pins("J5 L4", dir="i")),
            Subsignal("sdi", Pins("J7", dir="o")),
            Subsignal("sdo", Pins("K5", dir="i")),
            Subsignal("spc", Pins("J6", dir="o")),
            Subsignal("spc", Pins("J6", dir="o")),
            Attrs(io_standard="3.3-V LVCMOS")
        ),
        
        UARTResource(0,
            rx="B4", tx="A4", rts="B5", cts="A6", dtr="B6", dsr="A7",
            attrs=Attrs(io_standard="3.3-V LVCMOS"), role="dce"
        ),
    ]

    default_clk = "clk12"
    #default_rst = "reset"

    connectors = [
        Connector("j",    0, "D3  E1  C2  C1  D1  E3  F1  E4  H8  K10 H5  H4  J1  J2 "),
        Connector("j",    1, "L12 J12 J13 K11 K12 J10 H10 H13 G12 -   -   -   -   -  "),
        Connector("j",    2, "D2  -   B1 "),
        Connector("pmod", 0, "M3  L3  M2  M1  -   -   N3  N2  K2  K1  -   -  ")
    ]

    def toolchain_program(self, products, name):
        quartus_pgm = os.environ.get("QUARTUS_PGM", "quartus_pgm")
        with products.extract(f"{name}.sof") as bitstream_filename:
            subprocess.check_call([quartus_pgm, "--haltcc", "--mode", "JTAG",
                                   "--operation", "P;" + bitstream_filename])

class MAX1000Platform_32M(MAX1000Platform):
    device = "10M16SA"

if __name__ == "__main__":
    from .test.blinky import Blinky
    MAX1000Platform().build(Blinky(), do_program=True)
