from . import libbk8500 as lbk

def check_packet(packet, expected):
    assert bytes(packet) == bytes(expected)

def test_github_example_8500pyserial():
    check_packet(lbk.packet.RemoteOperation(enable_remote=True), [0xaa, 00, 0x20, 0x01, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 0xcb])
    check_packet(lbk.packet.Mode(lbk.packet.LimitModeEnum.CC), [0xaa,00,0x28,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xd2])
    check_packet(lbk.packet.Enable(False), [0xaa,00,0x21,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xcb])
    check_packet(lbk.packet.CurrentLevel(0.02), [0xaa,00,0x2a,0xc8,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0x9c])