import serial
import libbk8500 as lbk

class Device:
    def __init__(self, port, baud=9600):
        self.ser = serial.Serial(port=port, baudrate=baud)

    def command(self, packet):
        data = bytes(packet)
        assert len(data) == 26, "Packet serialized to wrong length"
        self.ser.write(data)
        status_data = self.ser.read(26)
        lbk.packet.Status.deserialize(status_data)

    def request(self, response_type):
        data = response_type.request()
        assert len(data) == 26, "Packet serialized to wrong length"
        self.ser.write(data)
        response_data = self.ser.read(26)
        response = response_type.deserialize(response_data)
        return response

    def enable_load(self, enable):
        self.command(lbk.packet.EnableLoad(enable))

    def enable_remote(self, enable):
        self.command(lbk.packet.RemoteOperation(enable))

    def set_limits(self, voltage, current, power):
        if voltage is not None:
            self.command(lbk.packet.MaximumVoltage(voltage))
        if current is not None:
            self.command(lbk.packet.MaximumCurrent(current))
        if power is not None:
            self.command(lbk.packet.MaximumPower(power))

    def trigger(self):
        self.command(lbk.packet.Trigger())

    def set_level(self, limit_mode, value):
        limit_mode = lbk.packet.LimitModeEnum(limit_mode)
        packet_type = {
            lbk.packet.LimitModeEnum.CC: lbk.packet.CurrentLevel,
            lbk.packet.LimitModeEnum.CV: lbk.packet.VoltageLevel,
            lbk.packet.LimitModeEnum.CW: lbk.packet.PowerLevel,
            lbk.packet.LimitModeEnum.CR: lbk.packet.ResistanceLevel,
        }[limit_mode]
        self.command(packet_type(value))
