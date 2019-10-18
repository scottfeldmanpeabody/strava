'''
Not tested yet

Requirement:
StravaAthlete methods must run without errors
'''

class TestStravaAthlete(unittest.TestCase):
    def test_strava_athlete(self):
        ath.check_directories()
        ath.add_athlete()
        ath.get_rides()
        self.assertIsNotNone(ride_ids)
        ath.get_segments()
        self.assertIsNotNone(ath)
        ath.get_efforts()
        self.assertIsNotNone(ath.effort_df)
        ath.get_seg_details()
        self.assertIsNotNone(ath.seg_details_df)

if __name__ == '__main__':
    unittest.main()
    
