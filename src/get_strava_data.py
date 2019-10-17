import numpy as np
import pandas as pd
import time
import datetime
from stravalib.client import Client
import os
from pathlib import Path

class StravaAthlete(object):
    '''
    Gathers data for a strava athelete given possession of the API token
    '''

    def __init__(self, token):
        self.token = token
        self.client = Client(access_token=self.token)
        self._athlete_name()

    def _athlete_name(self):
        this_athlete = self.client.get_athlete()
        first = this_athlete.firstname
        last = this_athlete.lastname
        return first + '_' + last

    def check_strava_dir(self):
        if os.path.basename(os.getcwd()) != 'strava':
            return print('Please navigate to strava directory before proceeding.')
        else:
            print('In strava directory.')
            pass
    
    def check_athlete_folder(self):
        try:
            os.chdir('data/'+self._athlete_name())
            print('Data for {0} to be stored in {1}'.format(
                self._athlete_name(),'data/'+self._athlete_name()))
            os.chdir(Path(os.getcwd()).parents[1])
        except:
            return print('Need to create directory first. use .add_athlete()')

    def check_directories(self):
        self.check_strava_dir()
        self.check_athlete_folder()

    def add_athlete(self):
        self.check_strava_dir()

        if os.path.isdir('data') == False:
            os.mkdir('data')
            print('data directory created')
        else:
            pass
        if os.path.isdir(os.path.join('data/',self._athlete_name())) == False:
            print('creating data/{} directory...'.format(self._athlete_name()))
            os.mkdir('data/' + self._athlete_name())
            print('data/{} directory created'.format(self._athlete_name()))
        else:
            print('data/{} directory already exists'.format(self._athlete_name()))
                 
        try: #try to load df
            self.ath_df = pd.read_csv('data/athletes.csv') 
            print('ath_df successfully loaded')
        except: #check that df isn't in memory
            # if ath_df in globals():
            #     print('ath_df already in memory')
            # else:
            #     ath_cols = ['firstname','lastname','city','state']
            #     ath_df = pd.DataFrame(columns = ath_cols)
            #     print('empty ath_df intialized')
            try:
                self.ath_df = self.ath_df 
                print('ath_df already in memory')
            except: #create empty df
                ath_cols = ['firstname','lastname','city','state']
                ath_df = pd.DataFrame(columns = ath_cols)
                print('empty ath_df intialized')
        
        ath_cols = ['firstname','lastname','city','state']
        athlete_dict = self.client.get_athlete().to_dict()
        self.ath_df = self.ath_df.append(
            {k:athlete_dict[k] for k in ath_cols if k in athlete_dict},ignore_index=True)
        self.ath_df = self.ath_df.drop_duplicates() #in case athlete was already added
        print('{0} {1} added to ath_df'.format(self.ath_df.firstname.iloc[-1], self.ath_df.lastname.iloc[-1]))
        self.ath_df.to_csv('data/athletes.csv', index=False)
        print('ath_df saved to data/athletes.csv')

    def get_rides(self):
        '''
        Downloads a csv of all activity ids associated with rides
        '''
        self.check_directories()

        try:
            self.ride_ids = pd.read_csv('data/'+self._athlete_name()+'/ride_ids.csv')
            print('ride_ids.csv successfully loaded.')
        except:
            print('Need to gather ride IDs...')
            try:
                os.chdir('data/'+self._athlete_name())
                print('data for {0} to be stored in {1}'.format(
                    self._athlete_name(),'data/'+self._athlete_name()))
                os.chdir(Path(os.getcwd()).parents[1])
            except:
                return print('Need to create directory first. Use .add_athlete()')
            activities = self.client.get_activities() 
            act_list = list(activities)
            print('Ride IDs successfully downloaded')
            ride_id_list = []
            for act in act_list:
                if act.type != 'Ride':
                    continue
                else:
                    ride_id_list.append(act.id)
            ride_ids = pd.DataFrame(ride_id_list)
            ride_ids.columns = ['ride_id']
            ride_ids.name = ride_ids
            ride_ids.to_csv('data/'+self._athlete_name()+'/ride_ids.csv', index=False)
            print('Ride IDs saved to data/{}/ride_ids.csv'.format(self._athlete_name()))
            self.ride_ids = ride_ids

    def check_dependency(self, df): 
        '''
        This has a problem with passing a df that isn't defined. In that 
        case it will get an error before it even runs. Leaving in for now
        in case I can fix it but will just code it individually. (It's not
        too redundant.
        '''
        try:
            df = df
        except NameError:
            return print('No'+df+'. Run appropriate method')

    def get_segments(self):
        '''
        Downloads .csv of rides and segment ids. Require ride_ids dataframe
        '''
        self.check_directories()

        ### replace with check_dependency(ride_ids) if I get that working
        try:
            self.ride_ids = self.ride_ids
        except:
            return print('No ride_ids data frame. Must run get_rides() method first')
        ###
        
        try:
            self.segments_df = pd.read_csv('data/'+self._athlete_name()+'/segments_df.csv')
            return print('segments_df successfully loaded')
        except:
            segment_cols = ['ride_name',
                            'ride_id',
                            'bike',
                            'ride_distance',
                            'ride_moving_time',
                            'ride_elapsed_time',
                            'ride_elevation_gain',
                            'ride_start_time',
                            'segment_id']
            self.segments_df = pd.DataFrame(columns = segment_cols)
            print('Empty segments_df created.')
        ride_index = 0
        remaining_rides = self.ride_ids.ride_id
        rides_left = len(remaining_rides)
        
        while ride_index <= rides_left:
            try:
                for ride in range(ride_index, rides_left):
                    activity = self.client.get_activity(self.ride_ids.ride_id[ride], include_all_efforts=True)
                    for segment in activity.segment_efforts:
                        try:
                            activity.gear.name
                            self.segments_df = self.segments_df.append(
                                {'ride_name' : activity.name,
                                'ride_id' : activity.id,
                                'bike' : activity.gear.name, 
                                'ride_distance' : activity.distance, 
                                'ride_moving_time' : activity.moving_time, 
                                'ride_elapsed_time' : activity.elapsed_time, 
                                'ride_elevation_gain' : activity.total_elevation_gain, 
                                'ride_start_time' : activity.start_date_local,
                                'segment_id' : segment.segment.id},
                                ignore_index=True)
                        except AttributeError: #if activity.gear.name is missing, skip it
                            self.segments_df = self.segments_df.append(
                                {'ride_name' : activity.name,
                                'ride_id' : activity.id,
                                'ride_distance' : activity.distance, 
                                'ride_moving_time' : activity.moving_time, 
                                'ride_elapsed_time' : activity.elapsed_time, 
                                'ride_elevation_gain' : activity.total_elevation_gain, 
                                'ride_start_time' : activity.start_date_local,
                                'segment_id' : segment.segment.id},
                                ignore_index=True)
                    ride_index += 1
                    if ride_index % 50 == 0:
                        print('Last ride downloaded: id:{} {}'.format(self.segments_df.tail(1).iloc[0,1],
                                                                    self.segments_df.tail(1).iloc[0,0]))
                        print('It is {0}. Segments for {1} rides downloaded. {2} rides to go'
                            .format(datetime.datetime.now().strftime("%H:%M"),
                                    ride_index, 
                                    rides_left-ride_index))
            except:
                wait = 0
                print('rate limit exceeded, need to wait 15')
                print('it is now {} minutes after the hour'.format(datetime.datetime.now().minute))
                time.sleep(60*16)
                print('trying again...')
        print('segments for all {} rides downloaded'.format(ride_index))
        self.segments_df.name = 'segments_df'
        self.segments_df.to_csv('data/'+self._athlete_name()+'/segments_df.csv', index=False)
        print('segments_df saved to data/{}/segments_df.csv'.format(self._athlete_name()))

    def get_efforts(self):
        '''
        Returns df of individual efforts on segements. Requires segments_df df.
        '''
        self.check_directories()
        
        ### replace with check_dependency(ride_ids) if I get that working
        try:
            self.segments_df = self.segments_df
        except:
            return print('No segments_df data frame. Must run get_segments() method first')
        ###
        
        try:
            self.efforts_df = pd.read_csv('data/'+self._athlete_name()+'/efforts_df.csv')
            return print('efforts_df successfully loaded.')
        except FileNotFoundError:
            try:
                self.efforts_df = self.efforts_df
                effort_segs = efforts_df.segment_id.unique()
                print('Appending to existing efforts df.')
            except:
                efforts_columns = ['segment_id',
                    'effort_id',
                    'name',
                    'start_date',
                    'moving_time',
                    'elapsed_time',
                    'average_heartrate',
                    'max_heartrate']
                self.efforts_df = pd.DataFrame(columns = efforts_columns)
                effort_segs = np.array([])
                print('Empty efforts_df created.')
            
            effort_segment_index = 0
            effort_segs_to_download = 1

            while effort_segment_index < effort_segs_to_download:
                
                effort_segment_index = 0
                
                remaining_effort_segs = list(np.setdiff1d(self.segments_df.segment_id,effort_segs))
                effort_segs_to_download = len(remaining_effort_segs)
                print('remaining segments to get efforts for: {}'.format(effort_segs_to_download))
                
                try:
                    for segment in remaining_effort_segs:
                        this_segment = list(self.client.get_segment_efforts(segment))
                        for this_effort in this_segment:
                            this_effort_dict = this_effort.to_dict()
                            this_effort_dict['segment_id'] = segment
                            this_effort_dict['effort_id'] = this_effort.id
                            self.efforts_df = self.efforts_df.append(
                                {k:this_effort_dict[k] for k in efforts_columns if k in this_effort_dict},
                                ignore_index=True)
                        effort_segment_index += 1
                        if effort_segment_index % 50 == 0:
                            print('Last segment downloaded: {0} {1}'.format(self.efforts_df.tail(1).iloc[0,0],
                                                                        self.efforts_df.tail(1).iloc[0,2]))
                            print('It is {0}. Efforts for {1} segments downloaded. {2} segments to go...'
                                .format(datetime.datetime.now().strftime("%H:%M"),
                                        effort_segment_index,
                                        effort_segs_to_download - effort_segment_index))
                except:
                    self.efforts_df.to_csv('data/'+self._athlete_name()+'/efforts_df.csv', index=False)
                    print('efforts_df.csv successfully saved.')
                    wait = 0
                    print('Rate limit exceeded, need to wait until the quarter hour')
                    print('It is now {} minutes after the hour'.format(datetime.datetime.now().minute))
                    time.sleep(60*16)
                    print('Trying again...')
            print('Efforts for all {} segments downloaded'.format(segment_index))
            self.efforts_df.to_csv('data/'+self._athlete_name()+'/efforts_df.csv', index=False)
            print('efforts_df.csv successfully saved.')

    def get_seg_details(self):
        '''
        Downloads .csv of segment details. Require segments_df dataframe
        '''
        self.check_directories()

        ### replace with check_dependency(ride_ids) if I get that working
        try:
            self.segments_df = self.segments_df
        except:
            return print('No ride_ids data frame. Must run get_rides() method first')
        ###

        try:
            self.seg_details_df = pd.read_csv('data/'+self._athlete_name()+'/seg_details_df.csv')
            return print('seg_details_df successfully loaded.')
        except FileNotFoundError:
            try:
                self.seg_details_df = self.seg_details_df
                print('Appending to existing seg_details df.')
            except AttributeError:
                seg_details_cols = ['segment_id',
                    'name',
                    'distance',
                    'average_grade',
                    'maximum_grade',
                    'elevation_high',
                    'elevation_low',
                    'total_elevation_gain',
                    'start_latitude',
                    'end_latitude',
                    'start_longitude',
                    'end_longitude',
                    'climb_category',
                    'city',
                    'state',
                    'country',
                    'effort_count',
                    'athlete_count',
                    'athlete_segment_stats',
                    'map']
                self.seg_details_df = pd.DataFrame(columns = seg_details_cols)
                seg_details_to_download = np.array([])
                print('Empty seg_details_df created.')
            
            segments_remaining = len(self.segments_df)
            seg_details_index = 0

            while seg_details_index < segments_remaining:
                seg_details_index = 0
                
                seg_details_remaining = list(np.setdiff1d(self.segments_df.segment_id,seg_details_to_download))
                seg_details_to_download = len(seg_details_remaining)
                print('remaining segments to get details for: {}'.format(seg_details_to_download))
                try:
                    for segment in seg_details_remaining:
                        this_segment_dict = self.client.get_segment(segment).to_dict()
                        this_segment_dict['segment_id'] = segment
                        self.seg_details_df = self.seg_details_df.append(
                            {k:this_segment_dict[k] for k in seg_details_cols if k in this_segment_dict},
                            ignore_index=True)
                        seg_details_index += 1
                        if seg_details_index % 50 == 0:
                            self.seg_details_df.to_csv('data/'+self._athlete_name()+'/seg_details_df.csv', index=False)
                            print('efforseg_details_dfts_df.csv successfully saved.')
                            print('Last segment downloaded: {0} {1}'.format(self.seg_details_df.tail(1).iloc[0,0],
                                                                        self.seg_details_df.tail(1).iloc[0,1]))
                            print('It is {0}. {1} segments downloaded. {2} segments to go...'
                                .format(datetime.datetime.now().strftime("%H:%M"),
                                        seg_details_index,
                                        segments_remaining - seg_details_index))
                except:
                    wait = 0
                    print('rate limit exceeded, need to wait 15 minutes')
                    print('it is now {} minutes after the hour'.format(datetime.datetime.now().minute))
                    time.sleep(60*16)
                    print('trying again...')
            print('all {} segments downloaded'.format(seg_details_index))
            self.seg_details_df.to_csv('data/'+self._athlete_name()+'/seg_details_df.csv', index=False)
            print('seg_details_df.csv successfully saved.')


