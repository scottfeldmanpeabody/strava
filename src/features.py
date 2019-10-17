#import numpy as np
#import pandas as pd



def unpack_dict_col(df, col, key):
    '''
    Given a DataFrame, df, with a column, col, that is populated by dictionaries,
    Takes one key from that dictionary and turns it into a column in itself in df
    '''
    import ast
    import numpy as np

    vals = df[col].apply(ast.literal_eval)
    lst = []
    for row in vals:
        lst.append(row[key])
    arr = np.array(lst)
    df[key] = arr
    return df

def curvy1(pline):
    '''
    Uses cosine distance normalized by actual distance between each
    pair of 3 points to quantify curviness
    '''
    from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
    import polyline
    import numpy as np

    waypoints = polyline.decode(pline)
    cos_dist = []
    dist = []
    for i in range(len(waypoints)-2):
        vectA = np.array(waypoints[i+1])-np.array(waypoints[i])
        vectB = np.array(waypoints[i+2])-np.array(waypoints[i+1])
        cos_dist.append(cosine_distances(np.array([vectA,vectB]))[0,1])
        
        distA = np.sqrt((waypoints[i][0]-waypoints[i+1][0])**2+(waypoints[i][1]-waypoints[i+1][1])**2)
        distB = np.sqrt((waypoints[i+1][0]-waypoints[i+2][0])**2+(waypoints[i+1][1]-waypoints[i+2][1])**2)
        dist.append(distA + distB)
    curve = []
    for i in range(len(dist)):
        curve.append(cos_dist[i]/dist[i])
    return np.mean(curve)

def curvy2(pline):
    '''
    Compares each pair of  3 points A, B, C, uses  (AB + BC - AC)/(AB + BC)
    to quantify curviness.
    '''
    from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
    import polyline
    import numpy as np
    
    waypoints = polyline.decode(pline)
    curve = []
    wp = []
    for i in range(len(waypoints)-2):
        wp.append([waypoints[i+2]])
        vectA = np.array(waypoints[i+1])-np.array(waypoints[i])
        vectB = np.array(waypoints[i+2])-np.array(waypoints[i])
        vectC = np.array(waypoints[i+2])-np.array(waypoints[i])
        
        distA = np.sqrt((waypoints[i][0]-waypoints[i+1][0])**2+(waypoints[i][1]-waypoints[i+1][1])**2)
        distB = np.sqrt((waypoints[i+1][0]-waypoints[i+2][0])**2+(waypoints[i+1][1]-waypoints[i+2][1])**2)
        distC = np.sqrt((waypoints[i][0]-waypoints[i+2][0])**2+(waypoints[i][1]-waypoints[i+2][1])**2)
        curve.append((distA + distB - distC)/(distA + distB))
    return np.mean(curve)