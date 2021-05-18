import enum
import struct
from .field import *

PACKET_STRUCT = '<BBB'


def calc_checksum(packet_bytes):
    return sum(byte for byte in packet_bytes) & 0xFF


class Packet:
    COMMAND_ID = None
    RESPONSE_ID = None
    PACKET_FORMAT = None
    FIELDS = []

    def serialize(self, *command_args):
        assert self.COMMAND_ID is not None, 'Packet cannot be serialized'
        struct_format = PACKET_STRUCT + self.PACKET_FORMAT
        assert struct.calcsize(struct_format) == 25, "Packet Format String is not 26 bytes long"
        assert len(command_args) == len(self.FIELDS), "Incorrect number of fields"
        processed_args = (field.serialize(value) for field, value in zip(self.FIELDS, command_args))
        address = self.address if self.address is not None else 0
        data = struct.pack(struct_format, 0xAA, address, self.COMMAND_ID, *processed_args)
        checksum = calc_checksum(data).to_bytes(1, 'big')
        return data + checksum

    @classmethod
    def deserialize(cls, packet_bytes):
        assert cls.RESPONSE_ID is not None, 'Packet cannot be deserialized'
        assert len(packet_bytes) == 26, "Packet Data is not 26 bytes long"
        struct_format = PACKET_STRUCT + cls.PACKET_FORMAT
        assert struct.calcsize(struct_format) == 25, "Packet Format String is not 26 bytes long"
        expect_checksum = calc_checksum(packet_bytes[0:24])
        actual_checksum = packet_bytes[25]
        assert expect_checksum == actual_checksum, "Checksum is incorrect"
        packet_data = struct.unpack(struct_format, packet_bytes[0:24])
        assert packet_data[0] == 0xAA, "Packet Magic is incorrect"
        address = packet_data[1]
        command_id = packet_data[2]
        assert cls.RESPONSE_ID == command_id, "Command ID is unexpected"
        data = packet_data[3:]
        assert len(data) == len(cls.FIELDS), "Incorrect number of fields"
        proccessed_args = (field.deserialize(data) for field, data in zip(cls.FIELDS, data))
        return cls.__init__(*proccessed_args, address)


class Status(Packet):
    RESPONSE_ID = 0x12
    PACKET_FORMAT = 'B21x'

    class Code(enum.IntEnum):
        INCORRECT_CHECKSUM = 0x90
        INCORRECT_PARAMETER = 0xA0
        UNRECOGNIZED_COMMAND = 0xB0
        INVALID_COMMAND = 0xC0
        SUCCESS = 0x80

    FIELDS = [EnumField(Code)]

    def __init__(self, status):
        self.status = Status.Code(status)

    def __str__(self):
        return f'Status({self.status})'


class RemoteOperation(Packet):
    COMMAND_ID = 0x20
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_remote, address=None):
        self.enable_remote = bool(enable_remote)
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_remote)

    def __str__(self):
        return f'RemoteOperation(enable_remote={self.enable_remote})'


class EnableLoad(Packet):
    COMMAND_ID = 0x21
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_load, address=None):
        self.enable_load = bool(enable_load)
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_load)

    def __str__(self):
        return f'EnableLoad({self.enable_load})'


class MaximumVoltage(Packet):
    COMMAND_ID = 0x22
    RESPONSE_ID = 0x23
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, volts, address=None):
        self.volts = volts
        self.address = address

    def __bytes__(self):
        return super().serialize(self.volts)

    def __str__(self):
        return f'MaximumVoltage({self.volts} V)'


class MaximumCurrent(Packet):
    COMMAND_ID = 0x24
    RESPONSE_ID = 0x25
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(10_000)]

    def __init__(self, amps, address=None):
        self.amps = amps
        self.address = address

    def __bytes__(self):
        return super().serialize(self.amps)

    def __str__(self):
        return f'MaximumCurrent({self.amps} A)'


class MaximumPower(Packet):
    COMMAND_ID = 0x26
    RESPONSE_ID = 0x27
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, watts, address=None):
        self.watts = watts
        self.address = address

    def __bytes__(self):
        return super().serialize(self.watts)

    def __str__(self):
        return f'MaximumPower({self.watts} W)'


class LimitModeEnum(enum.IntEnum):
    CC = 0
    CV = 1
    CW = 2
    CR = 3


class Mode(Packet):
    COMMAND_ID = 0x28
    RESPONSE_ID = 0x29
    PACKET_FORMAT = 'B21x'
    FIELDS = [EnumField(LimitModeEnum)]

    def __init__(self, mode, address=None):
        self.mode = mode
        self.address = address

    def __bytes__(self):
        return super().serialize(self.mode)

    def __str__(self):
        return f'Mode({self.mode})'


class CurrentLevel(Packet):
    COMMAND_ID = 0x2A
    RESPONSE_ID = 0x2B
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(10_000)]

    def __init__(self, amps, address=None):
        self.amps = amps
        self.address = address

    def __bytes__(self):
        return super().serialize(self.amps)

    def __str__(self):
        return f'CurrentLevel({self.amps} A)'


class VoltageLevel(Packet):
    COMMAND_ID = 0x2C
    RESPONSE_ID = 0x2D
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, volts, address=None):
        self.volts = volts
        self.address = address

    def __bytes__(self):
        return super().serialize(self.volts)

    def __str__(self):
        return f'VoltageLevel({self.volts} V)'


class PowerLevel(Packet):
    COMMAND_ID = 0x2E
    RESPONSE_ID = 0x2F
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, watts, address=None):
        self.watts = watts
        self.address = address

    def __bytes__(self):
        return super().serialize(self.watts)

    def __str__(self):
        return f'PowerLevel({self.watts} W)'


class ResistanceLevel(Packet):
    COMMAND_ID = 0x30
    RESPONSE_ID = 0x31
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, ohms, address=None):
        self.ohms = ohms
        self.address = address

    def __bytes__(self):
        return super().serialize(self.ohms)

    def __str__(self):
        return f'ResistanceLevel({self.ohms} Ω)'


class TransientOperationEnum(enum.IntEnum):
    CONTINUOUS = 0
    PULSE = 1
    TOGGLED = 2


class CurrentTransient(Packet):
    COMMAND_ID = 0x32
    RESPONSE_ID = 0x33
    PACKET_FORMAT = 'IHIHB9x'
    FIELDS = [ScaledField(10_000), ScaledField(10_000), ScaledField(10_000), ScaledField(10_000),
              EnumField(TransientOperationEnum)]

    def __init__(self, value_a, time_a, value_b, time_b, operation, address=None):
        self.value_a = value_a
        self.time_a = time_a
        self.value_b = value_b
        self.time_b = time_b
        self.operation = operation
        self.address = address

    def __bytes__(self):
        return super().serialize(self.value_a, self.time_a, self.value_b,
                                 self.time_b, self.operation)

    def __str__(self):
        return f'CurrentTransient({self.value_a} A @ {self.time_a} s -> {self.value_b} A @ {self.time_b} s, operation={self.operation})'


class VoltageTransient(Packet):
    COMMAND_ID = 0x34
    RESPONSE_ID = 0x35
    PACKET_FORMAT = 'IHIHB9x'
    FIELDS = [ScaledField(1000), ScaledField(10_000), ScaledField(1000), ScaledField(10_000),
              EnumField(TransientOperationEnum)]

    def __init__(self, value_a, time_a, value_b, time_b, operation, address=None):
        self.value_a = value_a
        self.time_a = time_a
        self.value_b = value_b
        self.time_b = time_b
        self.operation = operation
        self.address = address

    def __bytes__(self):
        return super().serialize(self.value_a, self.time_a, self.value_b,
                                 self.time_b, self.operation)

    def __str__(self):
        return f'VoltageTransient({self.value_a} V @ {self.time_a} s -> {self.value_b} V @ {self.time_b} s, operation={self.operation})'


class PowerTransient(Packet):
    COMMAND_ID = 0x36
    RESPONSE_ID = 0x37
    PACKET_FORMAT = 'IHIHB9x'
    FIELDS = [ScaledField(1000), ScaledField(10_000), ScaledField(1000), ScaledField(10_000),
              EnumField(TransientOperationEnum)]

    def __init__(self, value_a, time_a, value_b, time_b, operation, address=None):
        self.value_a = value_a
        self.time_a = time_a
        self.value_b = value_b
        self.time_b = time_b
        self.operation = operation
        self.address = address

    def __bytes__(self):
        return super().serialize(self.value_a, self.time_a, self.value_b,
                                 self.time_b, self.operation)

    def __str__(self):
        return f'PowerTransient({self.value_a} W @ {self.time_a} s -> {self.value_b} W @ {self.time_b} s, operation={self.operation})'


class ResistanceTransient(Packet):
    COMMAND_ID = 0x38
    RESPONSE_ID = 0x39
    PACKET_FORMAT = 'IHIHB9x'
    FIELDS = [ScaledField(1000), ScaledField(10_000), ScaledField(1000), ScaledField(10_000),
              EnumField(TransientOperationEnum)]

    def __init__(self, value_a, time_a, value_b, time_b, operation, address=None):
        self.value_a = value_a
        self.time_a = time_a
        self.value_b = value_b
        self.time_b = time_b
        self.operation = operation
        self.address = address

    def __bytes__(self):
        return super().serialize(self.value_a, self.time_a, self.value_b,
                                 self.time_b, self.operation)

    def __str__(self):
        return f'ResistanceTransient({self.value_a} Ω @ {self.time_a} s -> {self.value_b} Ω @ {self.time_b} s, operation={self.operation})'


class ListOperation(Packet):
    COMMAND_ID = 0x3A
    RESPONSE_ID = 0x3B
    PACKET_FORMAT = 'B21x'
    FIELDS = [EnumField(TransientOperationEnum)]

    def __init__(self, mode, address=None):
        self.mode = mode
        self.address = address

    def __bytes__(self):
        return super().serialize(self.mode)

    def __str__(self):
        return f'ListOperation({self.mode})'


class ListRepeat(Packet):
    COMMAND_ID = 0x3C
    RESPONSE_ID = 0x3D
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_repeat, address=None):
        self.enable_repeat = enable_repeat
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_repeat)

    def __str__(self):
        return f'ListRepeat({self.enable_repeat})'


class ListSteps(Packet):
    COMMAND_ID = 0x3E
    RESPONSE_ID = 0x3F
    PACKET_FORMAT = 'H20x'
    FIELDS = [IntField()]

    def __init__(self, num_steps, address=None):
        self.num_steps = num_steps
        self.address = address

    def __bytes__(self):
        return super().serialize(self.num_steps)

    def __str__(self):
        return f'ListSteps({self.num_steps})'


class StepCurrent(Packet):
    COMMAND_ID = 0x40
    RESPONSE_ID = 0x41
    PACKET_FORMAT = 'HIH14x'
    FIELDS = [IntField(), ScaledField(10_000), ScaledField(10_000)]

    def __init__(self, step_num, amps, seconds, address=None):
        self.step_num = step_num
        self.amps = amps
        self.seconds = seconds
        self.address = address

    def __bytes__(self):
        return super().serialize(self.step_num, self.amps, self.seconds)

    def __str__(self):
        return f'StepCurrent(Step #{self.step_num}: {self.amps} A @ {self.seconds} s)'


class StepVoltage(Packet):
    COMMAND_ID = 0x42
    RESPONSE_ID = 0x43
    PACKET_FORMAT = 'HIH14x'
    FIELDS = [IntField(), ScaledField(1000), ScaledField(10_000)]

    def __init__(self, step_num, volts, seconds, address=None):
        self.step_num = step_num
        self.volts = volts
        self.seconds = seconds
        self.address = address

    def __bytes__(self):
        return super().serialize(self.step_num, self.volts, self.seconds)

    def __str__(self):
        return f'StepVoltage(Step #{self.step_num}: {self.volts} V @ {self.seconds} s)'


class StepPower(Packet):
    COMMAND_ID = 0x44
    RESPONSE_ID = 0x45
    PACKET_FORMAT = 'HIH14x'
    FIELDS = [IntField(), ScaledField(1000), ScaledField(10_000)]

    def __init__(self, step_num, watts, seconds, address=None):
        self.step_num = step_num
        self.watts = watts
        self.seconds = seconds
        self.address = address

    def __bytes__(self):
        return super().serialize(self.step_num, self.watts, self.seconds)

    def __str__(self):
        return f'StepPower(Step #{self.step_num}: {self.watts} W @ {self.seconds} s)'


class StepResistance(Packet):
    COMMAND_ID = 0x46
    RESPONSE_ID = 0x47
    PACKET_FORMAT = 'HIH14x'
    FIELDS = [IntField(), ScaledField(1000), ScaledField(10_000)]

    def __init__(self, step_num, ohms, seconds, address=None):
        self.step_num = step_num
        self.ohms = ohms
        self.seconds = seconds
        self.address = address

    def __bytes__(self):
        return super().serialize(self.step_num, self.ohms, self.seconds)

    def __str__(self):
        return f'StepResistance(Step #{self.step_num}: {self.ohms} Ω @ {self.seconds} s)'


class ListFilename(Packet):
    COMMAND_ID = 0x48
    RESPONSE_ID = 0x49
    PACKET_FORMAT = '10s12x'
    FIELDS = [Field()]

    def __init__(self, file_name, address=None):
        self.file_name = file_name
        self.address = address

    def __bytes__(self):
        return super().serialize(self.file_name)

    def __str__(self):
        return f'ListFilename({self.file_name})'


class PartitionScheme(Packet):
    COMMAND_ID = 0x4A
    RESPONSE_ID = 0x4B
    PACKET_FORMAT = 'B21x'

    class Scheme(enum.IntEnum):
        File1Steps1000 = 1
        File2Steps500 = 2
        File4Steps250 = 4
        File8Steps120 = 8

    FIELDS = [EnumField(Scheme)]

    def __init__(self, scheme, address=None):
        self.scheme = scheme
        self.address = address

    def __bytes__(self):
        return super().serialize(self.scheme)

    def __str__(self):
        return f'PartitionScheme({self.scheme})'


class SaveListFile(Packet):
    COMMAND_ID = 0x4C
    PACKET_FORMAT = 'B21x'
    FIELDS = [IntField()]

    def __init__(self, location, address=None):
        self.location = location
        self.address = address

    def __bytes__(self):
        return super().serialize(self.location)

    def __str__(self):
        return f'SaveListFile(location={self.location})'


class LoadListFile(Packet):
    COMMAND_ID = 0x4D
    PACKET_FORMAT = 'B21x'
    FIELDS = [IntField()]

    def __init__(self, location, address=None):
        self.location = location
        self.address = address

    def __bytes__(self):
        return super().serialize(self.location)

    def __str__(self):
        return f'LoadListFile(location={self.location})'


class MinimumBatteryVoltage(Packet):
    COMMAND_ID = 0x4E
    RESPONSE_ID = 0x4F
    PACKET_FORMAT = 'I18x'
    FIELDS = [ScaledField(1000)]

    def __init__(self, volts, address=None):
        self.volts = volts
        self.address = address

    def __bytes__(self):
        return super().serialize(self.volts)

    def __str__(self):
        return f'MinimumBatteryVoltage({self.volts} V)'


class LoadOnTimer(Packet):
    COMMAND_ID = 0x50
    RESPONSE_ID = 0x51
    PACKET_FORMAT = 'H20x'
    FIELDS = [IntField]

    def __init__(self, seconds, address=None):
        self.seconds = seconds
        self.address = address

    def __bytes__(self):
        return super().serialize(self.seconds)

    def __str__(self):
        return f'LoadOnTimer({self.seconds} s)'


class EnableLoadOnTimer(Packet):
    COMMAND_ID = 0x52
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_timer, address=None):
        self.enable_timer = enable_timer
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_timer)

    def __str__(self):
        return f'EnableLoadOnTimer({self.enable_timer})'


class SetAddress(Packet):
    COMMAND_ID = 0x54
    PACKET_FORMAT = 'H20x'
    FIELDS = [IntField()]

    def __init__(self, new_address, address=None):
        self.new_address = new_address
        self.address = address

    def __bytes__(self):
        return super().serialize(self.new_address)

    def __str__(self):
        return f'SetAddress(0x{self.new_address:2X})'


class EnableLocalOverride(Packet):
    COMMAND_ID = 0x55
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_override, address=None):
        self.enable_override = bool(enable_override)
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_override)

    def __str__(self):
        return f'EnableLocalOverride({self.enable_override})'


class EnableRemoteSensing(Packet):
    COMMAND_ID = 0x56
    PACKET_FORMAT = 'B21x'
    FIELDS = [BoolField()]

    def __init__(self, enable_sensing, address=None):
        self.enable_sensing = bool(enable_sensing)
        self.address = address

    def __bytes__(self):
        return super().serialize(self.enable_sensing)

    def __str__(self):
        return f'EnableRemoteSensing({self.enable_sensing})'


class SelectTriggerSource(Packet):
    COMMAND_ID = 0x58
    RESPONSE_ID = 0x59
    PACKET_FORMAT = 'B21x'

    class Source(enum.IntEnum):
        IMMEDIATE = 0
        EXTERNAL = 1
        BUS = 2

    FIELDS = [EnumField(Source)]

    def __init__(self, trigger_source, address=None):
        self.trigger_source = trigger_source
        self.address = address

    def __bytes__(self):
        return super().serialize(self.trigger_source)

    def __str__(self):
        return f'SelectTriggerSource({self.trigger_source})'


class Trigger(Packet):
    COMMAND_ID = 0x5A
    PACKET_FORMAT = '22x'
    FIELDS = []

    def __init__(self, address=None):
        self.address = address

    def __bytes__(self):
        return super().serialize()

    def __str__(self):
        return f'Trigger()'


class SaveSettings(Packet):
    COMMAND_ID = 0x5B
    PACKET_FORMAT = 'B21x'
    FIELDS = [IntField()]

    def __init__(self, register_num, address=None):
        self.register_num = register_num
        self.address = address

    def __bytes__(self):
        return super().serialize(self.register_num)

    def __str__(self):
        return f'SaveSettings(register_num={self.register_num})'


class LoadSettings(Packet):
    COMMAND_ID = 0x5C
    PACKET_FORMAT = 'B21x'
    FIELDS = [IntField()]

    def __init__(self, register_num, address=None):
        self.register_num = register_num
        self.address = address

    def __bytes__(self):
        return super().serialize(self.register_num)

    def __str__(self):
        return f'LoadSettings(register_num={self.register_num})'


class SelectFunction(Packet):
    COMMAND_ID = 0x5D
    RESPONSE_ID = 0x5E
    PACKET_FORMAT = 'B21x'

    class Function(enum.IntEnum):
        FIXED = 0
        SHORT = 1
        TRANSIENT = 2
        LIST = 3
        BATTERY = 4

    FIELDS = [EnumField(Function)]

    def __init__(self, function, address=None):
        self.function = function
        self.address = address

    def __bytes__(self):
        return super().serialize(self.function)

    def __str__(self):
        return f'SelectFunction({self.function})'


class Measure(Packet):
    RESPONSE_ID = 0x5F
    PACKET_FORMAT = 'IIIBH7x'
    FIELDS = [ScaledField(1000), ScaledField(10_000), ScaledField(1000), BitField(8), BitField(10)]

    class OperationBits(enum.IntEnum):
        CALCULATE_DEMARCATION_COEF = 0
        WAITING_FOR_TRIGGER = 1
        REMOTE_CONTROL_ENABLED = 2
        OUTPUT_STATE = 3
        LOCAL_KEY_ENABLED = 4
        REMOTE_SENSING_ENABLED = 5
        LOAD_ON_TIMER_ENABLED = 6

    class DemandBits(enum.IntEnum):
        VOLTAGE_REVERSED = 0
        OVER_VOLTAGE = 1
        OVER_CURRENT = 2
        OVER_POWER = 3
        OVER_TEMP = 4
        NOT_CONNECT_REMOTE = 5
        CONSTANT_CURRENT = 6
        CONSTANT_VOLTAGE = 7
        CONSTANT_POWER = 8
        CONSTANT_RESISTANCE = 9

    def __init__(self, volts, amps, watts, operation_bits, demand_bits, address=None):
        self.volts = volts
        self.amps = amps
        self.watts = watts
        self.operation_bits = operation_bits
        self.demand_bits = demand_bits
        self.address = address

    def __bytes__(self):
        return super().serialize(self.volts, self.amps, self.watts, self.operation_bits, self.demand_bits)

    def __str__(self):
        return f'Measure({self.volts} V, {self.amps} A, {self.watts} W, operation={self.operation_bits}, demand={self.demand_bits})'


class Version(Packet):
    RESPONSE_ID = 0x6A
    COMMAND_FORMAT = '5sBB10s5x'
    FIELDS = [Field(), Field(), Field(), Field()]

    def __init__(self, model, firmware_major, firmware_minor, serial_number, address=None):
        self.model = model
        self.firmware_major = firmware_major
        self.firmware_minor = firmware_minor
        self.serial_number = serial_number
        self.address = address

    def __bytes__(self):
        return super().serialize(self.model, self.firmware_major, self.firmware_minor, self.serial_number)

    def __str__(self):
        return f'Version(model={self.model}, firmware={self.firmware_major}.{self.firmware_minor}, serial_num={self.serial_number})'


class Barcode(Packet):
    RESPONSE_ID = 0x6B
    COMMAND_FORMAT = '3s2s2s2s13x'
    FIELDS = [Field(), Field(), Field(), Field()]

    def __init__(self, identity, sub, version, year, address=None):
        self.identity = identity
        self.sub = sub
        self.version = version
        self.year = year
        self.address = address

    def __bytes__(self):
        return super().serialize(self.identity, self.sub, self.version, self.year)

    def __str__(self):
        return f'Barcode({self.identity}{self.sub}{self.version}{self.year})'
