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

def best_fit_slope_and_intercept(xs,ys):
    '''
    Used in plot_model_performance()
    '''
    m = (((np.mean(xs)*np.mean(ys)) - np.mean(xs*ys)) /
         ((np.mean(xs)*np.mean(xs)) - np.mean(xs*xs)))
    
    b = np.mean(ys) - m*np.mean(xs)
    
    return m, b

def plot_model_performance(y_test, y_hat, target_name = '', title = ''):
    '''
    Plots a comparison of y_test vs. y_hat. In a perfect model,
    it's a line with a slope of 1.
    '''
    
    print('RMSE = {:.4f}'.format(np.sqrt(mean_squared_error(y_test, y_hat))))
    print('R^2 = {:.4f}'.format(r2_score(y_test,y_hat)))

    m, b = best_fit_slope_and_intercept(y_test,y_hat)
    regression_line = [(m*x)+b for x in y_test]

    plt.scatter(y_test, y_hat, alpha = .5, s = 5, label = None)
    plt.plot(y_test,regression_line, c = 'red', linewidth = .8, label = ('Linear Fit'))
    plt.xlabel('Actual {}'.format(target_name))
    plt.ylabel('Predicted {}'.format(target_name))
    plt.legend()
    plt.annotate('y = {0:.2f}x +{1:.2f}'.format(m, b), xy=(0.05, 0.80), xycoords='axes fraction')
    plt.annotate('R-squared = %0.2f' % r2_score(y_test,y_hat), xy=(0.05, 0.70), xycoords='axes fraction')
    plt.annotate('RMSE = %0.2f' % np.sqrt(mean_squared_error(y_test, y_hat)), xy=(0.05, 0.60), xycoords='axes fraction')
    plt.title(title)

def plot_feature_importances(model):
    '''
    Feature importances of a random forest model.
    '''
    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]
    features = list(X.columns[indices])

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(X.shape[1]):
        print("{}. {}: ({:.1%})".format(f + 1, features[f], importances[indices[f]]))


    # Plot the feature importances of the forest
    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(X.shape[1]), importances[indices],
           color="lightblue", yerr=std[indices], align="center")
    plt.xticks(range(X.shape[1]), features, rotation = 40)
    plt.xlim([-1, X.shape[1]])
    plt.ylabel('Importance (%)')
    plt.xlabel('Feature')
    plt.show()