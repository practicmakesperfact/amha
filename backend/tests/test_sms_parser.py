import unittest
from backend.utils.sms_parser import parse_telebirr_sms, normalize_phone
from backend.utils.validators import validate_ethiopian_phone, parse_amount, format_currency

class TestSMSParser(unittest.TestCase):
    def test_typical_telebirr_sms_format1(self):
        sms = "Transaction of Birr 150.50 from 0911223344 to 0909425014 completed. Ref No. HF87291A at 12/07/2026 14:30:15."
        parsed = parse_telebirr_sms(sms)
        self.assertEqual(parsed.amount, 150.50)
        self.assertEqual(parsed.sender_phone, "0911223344")
        self.assertEqual(parsed.receiver_phone, "0909425014")
        self.assertEqual(parsed.reference_number, "HF87291A")
        self.assertEqual(parsed.transaction_date, "12/07/2026 14:30:15")

    def test_typical_telebirr_sms_format2(self):
        sms = "Your account has received Birr 500 from +251912345678. Ref: ABC123XYZ789. Date: 12-07-2026 18:00."
        parsed = parse_telebirr_sms(sms)
        self.assertEqual(parsed.amount, 500.0)
        self.assertEqual(parsed.sender_phone, "0912345678")
        self.assertIsNone(parsed.receiver_phone)  # not specified in this format
        self.assertEqual(parsed.reference_number, "ABC123XYZ789")
        self.assertEqual(parsed.transaction_date, "12-07-2026 18:00")

    def test_ethiopian_phone_normalization(self):
        self.assertEqual(normalize_phone("+251911223344"), "0911223344")
        self.assertEqual(normalize_phone("0911223344"), "0911223344")
        self.assertEqual(normalize_phone("251911223344"), "0911223344")
        self.assertIsNone(normalize_phone("12345"))

    def test_validators(self):
        self.assertTrue(validate_ethiopian_phone("0911223344"))
        self.assertTrue(validate_ethiopian_phone("0711223344"))
        self.assertFalse(validate_ethiopian_phone("0811223344"))
        self.assertFalse(validate_ethiopian_phone("123456789"))

        self.assertEqual(parse_amount("100"), 100.0)
        self.assertEqual(parse_amount("1,250.50"), 1250.50)
        self.assertIsNone(parse_amount("-50"))
        self.assertIsNone(parse_amount("abc"))

        self.assertEqual(format_currency(1234.56), "1,234.56 ETB")

if __name__ == "__main__":
    unittest.main()
