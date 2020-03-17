"""tl_struct.py -- custom struct."""
import struct
from bson.objectid import ObjectId
from enum import Enum, IntEnum, unique
import json

from common import hexDump, flatten, safe_unicode


class StructException(Exception):
    pass


@unique
class Endian(IntEnum):
    little = 0
    big = 1


@unique
class Ops(IntEnum):
    Stop = 1
    SetNativeEndian = 2
    SetLittleEndian = 3
    SetBigEndian = 4
    SetNetworkEndian = 5

    VarUInt8 = 11
    VarInt8 = 12
    VarUInt16 = 13
    VarInt16 = 14
    VarUInt32 = 15
    VarInt32 = 16
    VarBool = 17
    VarString = 18
    VarFloat = 19
    VarUnicodeString = 20
    VarDouble = 21
    VarObjectId = 22
    VarBinary = 23
    VarJSON = 24

    def isControlOp(self):
        return self.value <= 10

    def isVarOp(self):
        return self.value > 10


class StructImpl(object):
    dctOps = {
        ">": Ops.SetBigEndian,
        "<": Ops.SetLittleEndian,
        "!": Ops.SetNetworkEndian,
    }
    dctVars = {
        "B": Ops.VarUInt8,
        "b": Ops.VarInt8,
        "H": Ops.VarUInt16,
        "h": Ops.VarInt16,
        "L": Ops.VarUInt32,
        "l": Ops.VarInt32,
        "?": Ops.VarBool,
        "s": Ops.VarString,
        "f": Ops.VarFloat,
        "d": Ops.VarDouble,
        "u": Ops.VarUnicodeString,
        "o": Ops.VarObjectId,
        "y": Ops.VarBinary,
        "j": Ops.VarJSON,
    }

    def __init__(self, format_string):
        self.format_string = format_string
        self.opStream = []
        self.opArgs = []
        self.endian = Endian.big
        self.endian_char = ">"

    def _SetProcs(self):
        self.dctProcs = {
            Ops.SetBigEndian: self.cbSetBigEndian,
            Ops.SetLittleEndian: self.cbSetLittleEndian,
            Ops.SetNetworkEndian: self.cbSetNetworkEndian,
            Ops.SetNativeEndian: self.cbSetBigEndian,
            Ops.VarInt8: self.cbVarInt8,
            Ops.VarUInt8: self.cbVarUInt8,
            Ops.VarInt16: self.cbVarInt16,
            Ops.VarUInt16: self.cbVarUInt16,
            Ops.VarInt32: self.cbVarInt32,
            Ops.VarUInt32: self.cbVarUInt32,
            Ops.VarBool: self.cbVarBool,
            Ops.VarString: self.cbVarString,
            Ops.VarFloat: self.cbVarFloat,
            Ops.VarDouble: self.cbVarDouble,
            Ops.VarUnicodeString: self.cbVarUnicodeString,
            Ops.VarObjectId: self.cbVarObjectId,
            Ops.VarBinary: self.cbVarBinary,
            Ops.VarJSON: self.cbVarJSON,
            Ops.Stop: self.cbStop,
        }

    def parseFormat(self):
        repeatCount = 0
        self.opStream = []
        for ch in self.format_string:
            try:
                value = int(ch)
                repeatCount = repeatCount * 10 + value
                continue
            except ValueError:
                pass
            if ch in self.dctOps:
                self.opStream.append(self.dctOps[ch])
                self.opArgs.append(None)
                continue
            if repeatCount == 0:
                repeatCount = 1
            if ch in self.dctVars:
                var = self.dctVars[ch]
                if var in [Ops.VarString, Ops.VarBinary]:
                    self.opStream.append(var)
                    self.opArgs.append(repeatCount)
                else:
                    for _ in range(repeatCount):
                        self.opStream.append(var)
                        self.opArgs.append(None)
                repeatCount = 0
            else:
                raise StructException('Char "%c" not supported in Struct' % ch)
        self.opStream.append(Ops.Stop)

    def Process(self):
        for op, args in zip(self.opStream, self.opArgs):
            self.dctProcs[op](args)

    def cbSetLittleEndian(self, args):
        self.endian = Endian.little
        self.endian_char = "<"

    def cbSetBigEndian(self, args):
        self.endian = Endian.big
        self.endian_char = ">"

    def cbSetNetworkEndian(self, args):
        self.endian = Endian.big
        self.endian_char = "!"

    def cbStop(self, args):
        pass

    # abstracts below
    def cbVarUInt8(self, args):
        raise StructException("cbVarUInt8() not overloaded")

    def cbVarInt8(self, args):
        raise StructException("cbVarInt8() not overloaded")

    def cbVarUInt16(self, args):
        raise StructException("cbVarUInt16() not overloaded")

    def cbVarInt16(self, args):
        raise StructException("cbVarInt16() not overloaded")

    def cbVarUInt32(self, args):
        raise StructException("cbVarUInt32() not overloaded")

    def cbVarInt32(self, args):
        raise StructException("cbVarInt32() not overloaded")

    def cbVarBool(self, args):
        raise StructException("cbVarBool() not overloaded")

    def cbVarString(self, args):
        raise StructException("cbVarString() not overloaded")

    def cbVarFloat(self, args):
        raise StructException("cbVarFloat() not overloaded")

    def cbVarDouble(self, args):
        raise StructException("cbVarDouble() not overloaded")

    def cbVarUnicodeString(self, args):
        raise StructException("cbVarUnicodeString() not overloaded")

    def cbVarObjectId(self, args):
        raise StructException("cbVarObjectId() not overloaded")

    def cbVarBinary(self, args):
        raise StructException("cbVarBinary() not overloaded")

    def cbVarJSON(self, args):
        raise StructException("cbVarJSON() not overloaded")

    def __str__(self):
        return "args:%s" % [arg for arg in self.args]


class StructPack(StructImpl):
    def __init__(self, format_string, *args):
        super(StructPack, self).__init__(format_string)
        self.args = args
        self._SetProcs()
        self.index = 0
        self.binData = ""

    def pack(self):
        self.parseFormat()
        self.Process()

    def GetNextArg(self):
        value = self.args[self.index]
        self.index += 1
        return value

    def cbVarUInt8(self, args):
        try:
            self.binData += struct.pack("B", self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarUInt8() fail - %s" % err)

    def cbVarInt8(self, args):
        try:
            self.binData += struct.pack("b", self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarInt8() fail - %s" % err)

    def cbVarUInt16(self, args):
        try:
            self.binData += struct.pack("%cH" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarUInt16() fail - %s" % err)

    def cbVarInt16(self, args):
        try:
            self.binData += struct.pack("%ch" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarInt16() fail - %s" % err)

    def cbVarUInt32(self, args):
        try:
            self.binData += struct.pack("%cL" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarUInt32() fail - %s" % err)

    def cbVarInt32(self, args):
        try:
            self.binData += struct.pack("%cl" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarInt32() fail - %s" % err)

    def cbVarBool(self, args):
        try:
            self.binData += struct.pack("?", self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarBool() fail - %s" % err)

    def cbVarString(self, args):
        try:
            s = self.GetNextArg()
            self.binData += struct.pack(
                "%cH%ds" % (self.endian_char, args), args, s[:args]
            )
        except struct.error as err:
            raise StructException("cbVarString() fail - %s" % err)

    def cbVarFloat(self, args):
        try:
            self.binData += struct.pack("%cf" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarFloat() fail - %s" % err)

    def cbVarDouble(self, args):
        try:
            self.binData += struct.pack("%cd" % self.endian_char, self.GetNextArg())
        except struct.error as err:
            raise StructException("cbVarDouble() fail - %s" % err)

    def cbVarObjectId(self, args):
        try:
            obj = self.GetNextArg()
            self.binData += struct.pack("%c12s" % self.endian_char, obj.binary)
        except struct.error as err:
            raise StructException("cbVarObjectId() fail - %s" % err)

    def cbVarBinary(self, args):
        try:
            data = self.GetNextArg()
            self.binData += struct.pack("%c%ds" % (self.endian_char, args), data)
        except struct.error as err:
            raise StructException("cbVarBinary() fail - %s" % err)

    def cbVarJSON(self, args):
        try:
            obj = self.GetNextArg()
            json_string = json.dumps(obj)
            length = len(json_string)
            self.binData += struct.pack(
                "%cH%ds" % (self.endian_char, length), length, json_string
            )
        except struct.error as err:
            raise StructException("cbVarJSON() fail - %s" % err)


class StructUnpack(StructImpl):
    def __init__(self, format_string, binData):
        super(StructUnpack, self).__init__(format_string)
        self._SetProcs()
        self.index = 0
        self.binData = binData
        self.lstData = []

    def unpack(self):
        self.parseFormat()
        self.lstData = []
        self.Process()

    def _unpackData(self, name, fmt, byte_size):
        try:
            value, = struct.unpack(
                "%c%s" % (self.endian_char, fmt),
                self.binData[self.index : self.index + byte_size],
            )
            self.index += byte_size
            self.lstData.append(value)
        except struct.error as err:
            raise StructException("%s fail - %s" % (name, err))

    def cbVarUInt8(self, args):
        self._unpackData("cbVarUInt8", "B", 1)

    def cbVarInt8(self, args):
        self._unpackData("cbVarInt8", "b", 1)

    def cbVarUInt16(self, args):
        self._unpackData("cbVarUInt16", "H", 2)

    def cbVarInt16(self, args):
        self._unpackData("cbVarInt16", "h", 2)

    def cbVarUInt32(self, args):
        self._unpackData("cbVarUInt32", "L", 4)

    def cbVarInt32(self, args):
        self._unpackData("cbVarInt32", "l", 4)

    def cbVarBool(self, args):
        self._unpackData("cbVarBool", "?", 1)

    def cbVarString(self, args):
        try:
            length, = struct.unpack(
                "%cH" % self.endian_char, self.binData[self.index : self.index + 2]
            )
            self.index += 2
            s, = struct.unpack(
                "%ds" % length, self.binData[self.index : self.index + length]
            )
            self.index += length
            s = str(s).replace("\0", "")
            self.lstData.append(s)
        except struct.error as err:
            raise StructException("cbVarString() fail - %s" % err)

    def cbVarFloat(self, args):
        self._unpackData("cbVarFloat", "f", 4)

    def cbVarDouble(self, args):
        self._unpackData("cbVarDouble", "d", 8)

    def cbVarObjectId(self, args):
        try:
            length = 12
            sID, = struct.unpack("12s", self.binData[self.index : self.index + length])
            _id = ObjectId(sID)
            self.index += length
            self.lstData.append(_id)
        except struct.error as err:
            raise StructException("cbVarObjectId() fail - %s" % err)

    def cbVarBinary(self, args):
        try:
            data, = struct.unpack(
                "%c%ds" % (self.endian_char, args),
                self.binData[self.index : self.index + args],
            )
            self.index += args
            self.lstData.append(data)
        except struct.error as err:
            raise StructException("cbVarBinary() fail - %s" % err)

    def cbVarJSON(self, args):
        try:
            length, = struct.unpack(
                "%cH" % (self.endian_char), self.binData[self.index : self.index + 2]
            )
            self.index += 2
            s, = struct.unpack(
                "%ds" % length, self.binData[self.index : self.index + length]
            )
            self.index += length
            json_data = json.loads(s)
            self.lstData.append(json_data)
        except struct.error as err:
            raise StructException("cbVarJSON() fail - %s" % err)


class Struct(object):
    @staticmethod
    def pack(format_string, *args):
        st = StructPack(format_string, *args)
        st.pack()
        return st.binData

    @staticmethod
    def unpack(format_string, binData):
        st = StructUnpack(format_string, binData)
        st.unpack()
        return tuple(st.lstData)


if __name__ == "__main__":

    def test_multi_UInt8():
        test_values1 = [1, 5, 10, 100, 255]
        test_values2 = [10, 20, 30, 40, 50]
        fmt = "BB"
        size = 2
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_UInt16():
        test_values1 = [1, 5, 10, 100, 255]
        test_values2 = [10, 20, 30, 40, 50]
        fmt = "HH"
        size = 4
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_float():
        test_values1 = [1.0, 5.6, 10e6, 100e-9, 255.5678, 0]
        test_values2 = [10e9, 20e5, 30e-99, 40.1234, 50.567, 32767e-2]
        fmt = "ff"
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_double():
        test_values1 = [1.0, 5.6, 10e6, 100e-9, 255.5678, 0]
        test_values2 = [10e9, 20e5, 30e-99, 40.1234, 50.567, 32767e-2]
        fmt = "dd"
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_ObjectId():
        test_values1 = [ObjectId()]
        test_values2 = [ObjectId()]
        fmt = "oo"
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_string():
        test_values1 = ["Hello"]
        test_values2 = ["12345678901234567890"]
        fmt = "10s10s"
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    def test_multi_binary():
        test_values1 = ["\x00\x01\x02\x03"]
        test_values2 = ["\xff\xfe\xfd\xfc"]
        fmt = "4y4y"
        for values in zip(test_values1, test_values2):
            print("format:%s values:%s" % (fmt, values))
            pack_data = Struct.pack(fmt, values[0], values[1])
            hexDump(pack_data)
            tup = Struct.unpack(fmt, pack_data)
            print(tup)

    print("tl_struct testing")
    test_multi_UInt8()
    test_multi_UInt16()
    test_multi_float()
    test_multi_double()
    test_multi_ObjectId()
    test_multi_string()
    test_multi_binary()

    # lst_uints = [0,1,2,100,101,200,254,255]
    # for val in lst_uints:
    # fmt = 'B'
    # print 'format:%s val:%s' % (fmt, val)
    # data = Struct.pack(fmt, val)
    # hexDump(data)
    # lst = Struct.unpack(fmt, data)
    # print lst

    # lst_ints = [-127, -126, 0, 100, 127]
    # for val in lst_ints:
    # fmt = 'b'
    # print 'format:%s val:%s' % (fmt, val)
    # data = Struct.pack(fmt, val)
    # hexDump(data)
    # lst = Struct.unpack(fmt, data)
    # print lst

    # lst_uints = [0,1,2,100,101,200,254,255, 10000, 20000, 30000]
    # for val in lst_uints:
    # fmt = 'H'
    # print 'format:%s val:%s' % (fmt, val)
    # data = Struct.pack(fmt, val)
    # hexDump(data)
    # lst = Struct.unpack(fmt, data)
    # print lst
