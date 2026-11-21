import unittest
from space_telemetry import Telemetry

class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.t=Telemetry()
        self.sample=dict(latitude=-18.8,longitude=117.2,altitude=421.8,velocity=27572,
                         timestamp=1800000000,units='kilometers',visibility='daylight')
    def test_missing_and_expired_data_are_unavailable(self):
        self.assertFalse(self.t.snapshot(1800000000)['valid'])
        self.t.update(self.sample)
        self.assertTrue(self.t.snapshot(1800000045)['valid'])
        self.assertFalse(self.t.snapshot(1800000046)['valid'])
        self.assertFalse(self.t.snapshot(1799999990)['valid'])
    def test_units_and_invalid_values_are_rejected(self):
        for key,value in [('units','miles'),('latitude',91),('longitude',181),
                          ('altitude',float('nan')),('velocity',True),('timestamp',None)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.t.update(dict(self.sample,**{key:value}))
    def test_fields_preserve_units_timestamp_and_daylight(self):
        self.t.update(self.sample);v=self.t.snapshot(1800000001)
        self.assertEqual(v['sample'],self.sample['timestamp'])
        self.assertEqual(v['velocity'],27572)
        self.assertTrue(v['daylight']);self.assertTrue(v['model'])
if __name__=='__main__':unittest.main()
