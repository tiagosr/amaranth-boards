import os
import subprocess

from amaranth.build import *
from amaranth.vendor.lattice_ecp5 import *
from .resources import *


__all__ = ["Colorlight_i5_Platform"]


class Colorlight_i5_Platform(LatticeECP5Platform):
    device                 = "LFE5U-25F"
    package                = "BG381C"
    speed                  = "6"
    default_clk            = "clk25"

    resources = [
        Resource("clk25", 0, Pins("P3", dir="i"), Clock(25e6), Attrs(IO_TYPE="LVCMOS33")),

        *LEDResources(pins="U16", invert = True,
                      attrs=Attrs(IO_TYPE="LVCMOS33", DRIVE="4")),

        # SPIFlash (GD25Q16CSIG)   1x/2x speed
        Resource("spi_flash", 0,
            Subsignal("cs",   PinsN("R2", dir="o")),
            Subsignal("clk",  Pins("U3", dir="o")),             
            Subsignal("cipo", Pins("V2", dir="i")),             # Chip: DI/IO0
            Subsignal("copi", Pins("W2", dir="o")),             #       DO/IO1
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # EM638325BK-6H 8MB 
        SDRAMResource(0,
            clk="B9", we_n="A10", cas_n="A9", ras_n="B10",
            ba="B11 C8", a="B13 C14 A16 A17 B16 B15 A14 A13 A12 A11 B12",
            dq="B6  A5  A6  A7  C7  B8  B5  A8  D8  D7  E8  D6  C6  D5  E7  C5 "
               "C10 D9  E11 D11 C11 D12 E9  C12 E14 C15 E13 D15 E12 B17 D14 D13",
            attrs=Attrs(PULLMODE="NONE", DRIVE="4", SLEWRATE="FAST", IO_TYPE="LVCMOS33")
        ),

        # Broadcom B50612D Gigabit Ethernet Transceiver
        Resource("eth_rgmii", 0,
            Subsignal("rst",     PinsN("P4", dir="o")),
            Subsignal("mdc",     Pins("N5", dir="o")),
            Subsignal("mdio",    Pins("P5", dir="io")),
            Subsignal("tx_clk",  Pins("U19", dir="o")),
            Subsignal("tx_ctl",  Pins("P19", dir="o")),
            Subsignal("tx_data", Pins("U20 T19 T20 R20", dir="o")),
            Subsignal("rx_clk",  Pins("L19", dir="i")),
            Subsignal("rx_ctl",  Pins("M20", dir="i")),
            Subsignal("rx_data", Pins("P20 N19 N20 M19", dir="i")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

        # Broadcom B50612D Gigabit Ethernet Transceiver
        Resource("eth_rgmii", 1,
            Subsignal("rst",     PinsN("P4", dir="o")),
            Subsignal("mdc",     Pins("N5", dir="o")),
            Subsignal("mdio",    Pins("P4", dir="io")),
            Subsignal("tx_clk",  Pins("G1", dir="o")),
            Subsignal("tx_ctl",  Pins("K1", dir="o")),
            Subsignal("tx_data", Pins("G2 H1 J1 J3", dir="o")),
            Subsignal("rx_clk",  Pins("H2", dir="i")),
            Subsignal("rx_ctl",  Pins("P2", dir="i")),
            Subsignal("rx_data", Pins("K2 L1 N1 P1", dir="i")),
            Attrs(IO_TYPE="LVCMOS33")
        ),

    ]
    connectors = [
        # SODIMM edge top
        Connector("j", 1, 
                  "-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   U16 -   "
                  "-   -   K18 C18 -   -   T18 R18 R17 P17 M17 T17 U18 U17 P18 N17 N18 M18 L20 L18 K20 K19 J20 J19 H20 G20 "
                  "G19 F20 F19 E20 -   -   E19 D20 D19 C20 B20 B19 B18 A19 C17 A18 D3  C4  B4  C3  E3  A3  C2  B1  C1  D2  "
                  "D1  E2  E1  F2  -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   "),

        # SODIMM edge bottom
        Connector("j", 2, 
                  "-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   R1  T1  "
                  "U1  Y2  W1  V1  M1  -   N2  N3  T2  M3  T3  R3  N4  M4  L4  L5  P16 J16 J18 J17 H18 H17 G18 H16 F18 G16 "
                  "E18 F17 F16 E16 -   -   E17 D18 D17 G5  D16 F5  E6  E5  F4  E4  F1  F3  G3  H3  H4  H5  J4  J5  K3  K4  "
                  "K5  B3  A2  B2  -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   "),
    ]

    @property
    def required_tools(self):
        return super().required_tools + [
            "openFPGALoader"
        ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = dict(ecppack_opts="--compress")
        overrides.update(kwargs)
        return super().toolchain_prepare(fragment, name, **overrides)

    def toolchain_program(self, products, name):
        tool = os.environ.get("OPENFPGALOADER", "openFPGALoader")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([tool, "-c", "ft232", "-m", bitstream_filename])

class Colorlight_i5_ExtBoard_Platform(Colorlight_i5_Platform):
    resources = Colorlight_i5_Platform.resources + [
        UARTResource(
            rx="J17", tx="H18",
            attrs=Attrs(IO_TYPE="LVCMOS33")
        ),
        
        Resource("hdmi_tx", 0,
            Subsignal("d", DiffPairs("G19 E20 C20", "H20 F19 D19", dir="o"),
                      Attrs(IO_TYPE="TMDS_33")),
            
            Subsignal("cklk", DiffPairs("J19", "K19", dir="o"),
                      Attrs(IO_TYPE="TMDS_33"))
        )
    ]

    connectors = [
        Connector("p", 2,
                  "- - U16 C18 R18 P17 T17 - U17 - - N17 M18 L18 J20 "
                  "- - K18 T18 R17 M17 U18 - P18 - - N18 L20 K20 G20 "),
        Connector("p", 3,
                  "- - F20 B20 B18 C17 D3  - B4  - - E3  C2  C1  D1  "
                  "- - D20 B19 A19 A18 C4  - C3  - - A3  B1  D2  E2  "),

        Connector("p", 4,
                  "- - F2  F1  G3  H4  J4  - K3  - - K5  B3  E19 -   "
                  "- - E1  E4  F3  H3  H5  - J5  - - A2  K4  B2  -   "),

        Connector("p", 5,
                  "- - E5  F5  G5  D18 E16 - F17 - - G16 H16 H17 J17 "
                  "- - F4  E6  D16 D17 E17 - F16 - - E18 F18 G18 H18 "),

        Connector("p", 6,
                  "- - J16 L5  M4  R3  M3  - N3  - - M1  W1  U1  R1  "
                  "- - J18 P16 L4  N4  T3  - T2  - - N2  V1  Y2  T1 ")
    ]

if __name__ == "__main__":
    from .test.blinky import *
    Colorlight_i5_Platform().build(Blinky(), do_program=True)
