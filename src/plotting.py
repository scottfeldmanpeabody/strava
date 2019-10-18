from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels
from src.features import curvy1, curvy2

def plot_confusion_matrix(y_true, y_pred, classes, ax,
                          normalize=False,
                          title=None,
                          cmap=plt.cm.Blues):
    '''
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    '''
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    #classes = classes[unique_labels(y_true, y_pred)]
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#         print("Normalized confusion matrix")
#     else:
#         print('Confusion matrix, without normalization')

#     print(cm)

    #fig, ax = plt.subplots() 
    fig = plt.subplots()[0] 
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    #fig.tight_layout()
    return ax

def plot_segment_map(df, seg, ax):
    '''
    Plots a polyline using lat/long as x/y. Note, this is not technically correct, but 
    works okay since the segments are short. Also calculates and displays the two
    curvy metrics.
    '''

    row = df.index[df.segment_id == seg][0]
    xy = polyline.decode(df.polyline[row])
    
    name = df.name[row]
    curve1 = curvy1(df.polyline[row])
    curve2 = curvy2(df.polyline[row])
    
    x = []
    y = []
    for i in xy:
        x.append(i[1])
        y.append(i[0])
    
    xrange = max(x)-min(x)
    yrange = max(y)-min(y)
    if xrange > yrange:
        range = xrange
    else:
        range = yrange
    
    #fig, ax = plt.subplots(figsize = (6,6)) 
    
    ax.plot(x, y, linestyle='-', marker='o', ms = 3)
    ax.plot(x[0], y[0], marker='o', c = 'green', ms = 15, label = 'start')
    ax.plot(x[-1], y[-1], marker='o', color = 'red', ms = 15, label = 'end')
    ax.set_xlim(min(x) - range*0.1, min(x) + range*1.1)
    ax.set_ylim(min(y) - range*0.1, min(y) + range*1.1)
    ax.tick_params(axis='x', rotation=90)
    ax.annotate('start', xy=(x[0],y[0]))#, xytext=(.00000000000003, .00000000000003),arrowprops=dict(facecolor='black', shrink=0.05))
    ax.annotate('end', xy=(x[-1],y[-1]))
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_title('{0} \n curvy1: {1:.1f} \n curvy2: {2.2%}'.format(name, curve1, curve2))
    return ax

def plot_polyline(pline):
    curve1 = curvy1(pline)
    curve2 = curvy2(pline)
    
    xy = polyline.decode(pline)
    x = []
    y = []
    for i in xy:
        x.append(i[1])
        y.append(i[0])
    
    xrange = max(x)-min(x)
    yrange = max(y)-min(y)
    if xrange > yrange:
        range = xrange
    else:
        range = yrange
    
    fig, ax = plt.subplots(figsize = (6,6))    
    
    ax.plot(x, y, linestyle='-', marker='o', ms = 1)
    ax.plot(x[0], y[0], marker='o', c = 'green', ms = 15, label = 'start')
    ax.plot(x[-1], y[-1], marker='o', color = 'red', ms = 15, label = 'end')
    ax.set_xlim(min(x) - range*0.1, min(x) + range*1.1)
    ax.set_ylim(min(y) - range*0.1, min(y) + range*1.1)
    ax.tick_params(axis='x', rotation=90)
    ax.annotate('start', xy=(x[0],y[0]))
    ax.annotate('end', xy=(x[-1],y[-1]))
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_title('curvy1: {0:.1f} \n curvy2: {1:.2%}'.format(curve1,curve2))