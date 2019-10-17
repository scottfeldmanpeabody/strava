def meters_to_miles(df, col):
    df[col] = df[col].apply(lambda x : x * 0.000621371)
    
def meters_to_feet(df, col):
    df[col] = df[col].apply(lambda x : x * 3.28084)
    
def remove_meters_label(df, col):
    df[col] = df[col].str[:-2]
    df[col] = df[col].astype(float)
    
def convert_ride_time(df, col):
    df[col] = df[col].str[-8:]
    df[df[col] == '00000000'] = np.nan
    df[col] = pd.to_datetime(df[col], format='%H:%M:%S')
    df[col] = [datetime.datetime.time(d) for d in df[col]]

def get_sec(time_str):
    '''
    Converts H:M:S to seconds.
    '''
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)