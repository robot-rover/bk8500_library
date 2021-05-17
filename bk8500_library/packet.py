import struct
import enum

PACKET_STRUCT = 'BBB'

def calc_checksum(packet_bytes):
    return sum(byte for byte in packet_bytes) & 0xFF

class Packet:
    def __init__(self, command_id, command_str, command_args, address=None):
        struct_format = PACKET_STRUCT + command_str
        assert struct.calcsize(struct_format) == 25, "Packet Command String is not 26 bytes long"
        if address is None:
            address = 0
        data = struct.pack(struct_format, 0xAA, address, command_id, *command_args)
        checksum = calc_checksum(data).to_bytes(1, 'big')
        self.data = data + checksum

class Response:
    def __init__(self, packet_bytes, command_id=None):
        assert len(packet_bytes) == 26, "Packet Data is not 26 bytes long"
        assert packet_bytes[0] == 0xAA, "Packet Magic is incorrect"
        self.address = packet_bytes[1]
        self.command_id = packet_bytes[2]
        if command_id is not None:
            assert command_id == self.command_id, "Command ID is unexpected"
        expect_checksum = calc_checksum(packet_bytes[0:24])
        actual_checksum = packet_bytes[25]
        assert expect_checksum == actual_checksum, "Checksum is incorrect"
        self._command_data = packet_bytes[3:24]

class StatusResponse(Response):
    class Status(enum.IntEnum):
        INCORRECT_CHECKSUM = 0x90
        INCORRECT_PARAMETER = 0xA0
        UNRECOGNIZED_COMMAND = 0xB0
        INVALID_COMMAND = 0xC0
        SUCCESS = 0x80

    def __init__(self, packet_bytes):
        super().__init__(packet_bytes)

        self.status = StatusResponse.Status(self._command_data[0])

class DataResponse(Response):
