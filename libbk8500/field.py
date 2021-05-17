from bitarray.util import int2ba, ba2int


class Field:
    def serialize(self, value):
        return value

    def deserialize(self, data):
        return data


class BitField(Field):
    def __init__(self, length):
        self.length = length

    def serialize(self, value):
        return int2ba(value, self.length, 'little')

    def deserialize(self, data):
        return ba2int(data)


class IntField:
    def serialize(self, value):
        return int(value)

    def deserialize(self, data):
        return data


class BoolField(Field):
    def serialize(self, value):
        return 1 if value else 0

    def deserialize(self, data):
        return bool(data)


class ScaledField(Field):
    def __init__(self, scalar):
        self.scalar = scalar

    def serialize(self, value):
        return int(self.scalar * value)

    def deserialize(self, data):
        return data / self.scalar


class EnumField(Field):
    def __init__(self, enum):
        self.enum = enum

    def serialize(self, value):
        return int(value)

    def deserialize(self, data):
        return self.enum.__init__(data)
