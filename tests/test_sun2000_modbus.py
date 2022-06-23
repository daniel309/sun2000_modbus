import unittest
from unittest.mock import patch
import sun2000mock

from pymodbus.exceptions import ModbusIOException
from sun2000_modbus.sun2000_modbus import Sun2000
from sun2000_modbus.datatypes import decode, DataType
from sun2000_modbus.registers import InverterEquipmentRegister


class TestDataTypes(unittest.TestCase):
    def test_decode_string(self):
        value = b'SUN2000-10KTL-M1\x00\x00\x00\x00SUN2000-12'
        decoded = decode(value, DataType.STRING)
        self.assertEqual(decoded, 'SUN2000-10KTL-M1\x00\x00\x00\x00SUN2000-12')

    def test_decode_uint16_be(self):
        value = b'\x04\xD2'
        decoded = decode(value, DataType.UINT16_BE)
        self.assertEqual(decoded, 1234)

    def test_decode_uint32_be(self):
        value = b'\x07\x5B\xCD\x15'
        decoded = decode(value, DataType.UINT32_BE)
        self.assertEqual(decoded, 123456789)

    def test_decode_int16_be(self):
        value = b'\xfb\x2e'
        decoded = decode(value, DataType.INT16_BE)
        self.assertEqual(decoded, -1234)

    def test_decode_int32_be(self):
        value = b'\xf8\xa4\x32\xeb'
        decoded = decode(value, DataType.INT32_BE)
        self.assertEqual(decoded, -123456789)

    def test_decode_bitfield16(self):
        value = b'\x3e\x22'
        decoded = decode(value, DataType.BITFIELD16)
        self.assertEqual(decoded, '0011111000100010')

    def test_decode_bitfield32(self):
        value = b'\x3e\x22\xaf\x45'
        decoded = decode(value, DataType.BITFIELD16)
        self.assertEqual(decoded, '00111110001000101010111101000101')

    def test_decode_multidata(self):
        value = b'\x3e\x22\xaf\x45'
        decoded = decode(value, DataType.MULTIDATA)
        self.assertEqual(decoded, b'\x3e\x22\xaf\x45')

    def test_decode_invalid(self):
        value = b'\x3e'
        self.assertRaises(ValueError, decode, value, 'invalid')


class TestSun2000(unittest.TestCase):
    def setUp(self) -> None:
        self.test_inverter = Sun2000(host='192.168.8.1', port=123, timeout=3, wait=0, unit=1)

    def test_init(self):
        self.assertEqual(self.test_inverter.inverter.host, '192.168.8.1')
        self.assertEqual(self.test_inverter.inverter.port, 123)
        self.assertEqual(self.test_inverter.inverter.timeout, 3)
        self.assertEqual(self.test_inverter.wait, 0)
        self.assertEqual(self.test_inverter.unit, 1)
        self.assertEqual(self.test_inverter.connected, False)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_connect_success(self):
        self.test_inverter.connect()
        self.assertTrue(self.test_inverter.connected)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_fail
    )
    def test_connect_fail(self):
        self.test_inverter.connect()
        self.assertFalse(self.test_inverter.connected)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_fail
    )
    def test_read_raw_value_string_from_disconnected_unit(self):
        self.test_inverter.connect()
        self.assertRaises(ValueError, self.test_inverter.read_raw_value, InverterEquipmentRegister.Model)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers_fail
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_raw_value_string_from_unavailable_unit(self):
        self.test_inverter.connect()
        self.assertRaises(ModbusIOException, self.test_inverter.read_raw_value, InverterEquipmentRegister.Model)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_raw_value_string(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_raw_value(InverterEquipmentRegister.Model)
        self.assertEqual(result, 'SUN2000')

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_raw_value_uint16be(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_raw_value(InverterEquipmentRegister.ModelID)
        self.assertEqual(result, 429)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_raw_value_uint32be(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_raw_value(InverterEquipmentRegister.RatedPower)
        self.assertEqual(result, 10000)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_uint32be(self):
        self.test_inverter.connect()
        result = self.test_inverter.read(InverterEquipmentRegister.RatedPower)
        self.assertEqual(result, 10.0)

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_formatted_uint32be(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_formatted(InverterEquipmentRegister.RatedPower)
        self.assertEqual(result, "10.0 kW")

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_raw_value_bitfield16(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_raw_value(InverterEquipmentRegister.State1)
        self.assertEqual(result, '0000000000000110')

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_bitfield16(self):
        self.test_inverter.connect()
        result = self.test_inverter.read(InverterEquipmentRegister.State1)
        self.assertEqual(result, '0000000000000110')

    @patch(
        'pymodbus.client.sync.ModbusTcpClient.read_holding_registers', sun2000mock.mock_read_holding_registers
    )
    @patch(
        'pymodbus.client.sync.ModbusTcpClient.connect', sun2000mock.connect_success
    )
    def test_read_formatted_bitfield16(self):
        self.test_inverter.connect()
        result = self.test_inverter.read_formatted(InverterEquipmentRegister.State1)
        self.assertEqual(result, '0000000000000110')
