from src.get_strava_data import StravaAthlete

kp = StravaAthlete(token = 'de05acb15a17c6dfa6008f7d6e122b328e57b228')
print('loaded StavaAthelete as kp')

kp.check_directories()

kp.get_rides()
kp.get_segments()
kp.get_efforts()
#kp.get_seg_details()