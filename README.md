# Creating New Functionality with Strava Data

## Introduction

![](https://www.ride25.com/wp-content/uploads/2014/10/strava_rgb_logotype.png "Strava Logo")

[Strava](https://www.strava.com) is an app at the juxtiposition of social networking, fitness, and GPS tracking. Used mostly by cyclists and runners, Strava allows athletes to upload GPS tracks of their workouts and share them with their friends (and the rest of the internet). The unique feature Strava has is user-defined "segments" which function as short, virtual racecourses where an athelete can compare times against themselves in order to try to get a PR (personal record), and others for the course record (also known as the K/QOM -- King/Queen of the Mountain for cycling).

I've used Strava for many years, mostly as a cyclist. In addition to using it for ride tracking and competition (even if only in my head), I've also used it to find new places to ride and estimate how long a ride will take me. 

### Which bike should I bring?

Strava provides a "Segment Explore" function that can help identify places to ride. One bit of functionality it lacks is whether a segment is primarily for road biking or mountain biking. 

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/strava_map_golden.png "Some Strava segments in Golden")
*Strava's segment explorer centered on Golden, CO.*


* **J. 32nd Ave, Youngfield to ...[Ford]** clearly sounds like a road biking route, just from it's title.
* Using similar logic **E. Lower LMR to Upper LMR [Lookout Mountain Road]**, sounds like it would be a road biking route as well, but it's most certainly a mountain bike segment as you could tell if you cross-referenced with the [satellite image from Google Maps](https://www.google.com/maps/@39.7400833,-105.235872,1521m/data=!3m1!1e3).
* The more imaginatively named **D. Suck It Up Ascent** looks like a smooth, albeit dirt road from the [satellite view](https://www.google.com/maps/@39.7790999,-105.2262892,797m/data=!3m1!1e3), but it's most certainly a route you would rather do on a mountain bike.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/Lower_LMR_to_Upper_LMR.png)</br>
*Lower LMR to Upper LMR definitely is not on Lookout Mountain Road*

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/Suck_It_Up_Ascent.png)</br>
*The appropriate bike to ride on Suck It Up Ascent isn't as clear from the satellite image*


While I can think of other ways ot solve this problem (including Strava just crowd sourcing the groupings from its users), I wanted to see if I could model road bike vs. mountain bike segments.

### How long will it take?

While many segements are rather short, a mile or less, some map out an entire ride:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/buffalo_brain_loop.png) <br/>
*[The Buffalo Brain Loop](https://www.strava.com/segments/2490347) is almost a complete ride minus the short trip to the parking lot*


Had I never ridden this before, it would be nice to know how long it will take me to complete this ride. Or, alternatively, what's a good time with which to challenge myself with? Strava allows you to view the "leaderboard" and see everyone's best time on a given segment. And it even allows you to filter down to atheletes you are following. But still, how do I know how an average time of mine will compare to any one other rider's best time? Below, I've developed a model that will estimate your time on a segment you haven't ridden in comparison to a rider you have ridden with before

## Data collection

Strava has an [API](http://developers.strava.com) which, in a very "there's an app for that" moment, can be accessed with the [stravalib](https://pythonhosted.org/stravalib/) library. Setting up a Flask site to use the API is isn't that hard, but it's not that easy, either. [hozn's Github repo](https://github.com/hozn/stravalib) provides a good walkthrough on how to do this. Unfortunately, the rates you can pull data are throttled significantly, and the data you can gather is limited to users who have password authorized your app. 

Fortunately, I have recorded a couple thousand myself and my wife, K, has hundreds more, so this provided the fodder I needed for the modeling done below.

[get_strava_data.py](https://github.com/scottfeldmanpeabody/strava/blob/master/src/get_strava_data.py) creates a StravaAthlete class and allows you to download data for that athlete. It also creates a directory structure to store the data in /strava/data/user_name/ once you've created the /strava directory.

The data pipeline looked like athlete -> rides recorded -> segments ridden -> segment efforts (attempts) & segment details.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/seg_details_df.png)
*Example segment details.*

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/efforts_df.png)
*Example segment efforts.*


## Which Bike Should I Bring? - Classification Modeling

Firstly, there are far too many categories of bikes these days (see [wikipedia](https://en.wikipedia.org/wiki/List_of_bicycle_types) for what's still probably an incomplete list), but for an average Strava user, it breaks down to road bike or mountain bike.

#### Classifying my target

Strava lets you label your gear for each rider. In order to determine whether a segment is a road bike or a mountain bike segment, I was able to use the labeled bike for each ride.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/attempts_by_bike.png)</br>
*Count of Strava segments ridden on each bike. Note, there are sometimes dozens of segments per ride, hence the large y- scale in the 10,000's*


While it's obvious to the  that "Road", "Carbon Road", and "Road + Burley" (a Burley is a kid trailer), are all road bikes, knowing my own mildy clever bike names, I grouped all of the bikes into the two categories of interest. 

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/bike_names.png)
*Rad names for rad bikes.*


I've always estimated that I'm close to 50/50 with road vs. mountain biking, but never looked at it quantitatively before. It turns out that's the case, and the data set rather well balanced by segment attempts without me doing anything:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/attempts_by_bike_type.png)</br>
*Reasonably balanced data set without any over/under sampling.*


Even though the data is labeled by bike, which has been transformed into bike type, not all segments are cleanly separated. Sometimes I ride my moutain bike to the trails and in the process traverse road segments. Sometimes I decide to be a bit of an idiot and ride my road bike on singletrack. The way I handled this was to calculate the percentage of road bike use on each segment. 0% = entirely mountain bike use, 100% = entirely road bike use. Most of the segments are "pure," but for those within 30% of either end, I defined them by 0-30% = mountain bike, and 70-100% = road bike. 30%-70% was dropped from the dataset.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/distribution_of_segments_by_biketype.png)</br>
*Classifying segments as road bike or mountain bike segments by taking the manjority of bike type that was used. The middle 40% is ambiguous and was dropped from the dataset. Blue lines show the original distribution of % road bike use on each segment, and the orange line shows the distribution when each segment was forced to either mountain or road use.*


#### Feature engineering and selection

For each segment, Strava provides a number of features, not all of which are independent of each other. For instance, between:
* Distance
* Elevation Low
* Elevation High
* Average Grade

There are really only 3 independent variables. Knowning distance and elevation change, one could calculate the average grade.

For each segment attempt (a.k.a. effort), I also have a time. I calculated an average speed for each effort using (segment distance)/(effort time). For many efforts I have both an average and max heart rate. The max heart rate tends to be bogus most of the time due to errors from the heart rate monitor. 

Another piece of data you can get from Strava is the google polyline for the segment. As with the Strava API, [there's library for that](https://pypi.org/project/polyline/). A google polyline is a string that can be decoded into a list of (latitude, longitude) tuples with polyline.decode(). These points can then be plotted to give a map of the entire segment. I used each series of 3 points to get a "curviness" metric out of the polyline. An example of three points is shown below:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/defining_curvy.png)</br>
*Diagram for defining curvy metrics from the polyline. Segments AB and BC are consecutive points on the map. AC is a construction used in the definition of curvy2 (def. below).*


Two metrics for curviness were developed as curvy1() and curvy2() in the [features.py](https://github.com/scottfeldmanpeabody/strava/blob/master/src/features.py) script:
1. **curvy1:** uses the cosine difference between AB and BC, then divides by the total length AB + length BC. This normalization is needed due to not all polyline segments being the same length. The resulting units are inverse meters.
2. **curvy2:** uses the ratio (length AB + length BC - length AC) / (length AB + length BC). This metric is unitless and can be viewed as a percent further distance that you traveled along the path A -> B -> C rather than had you gone directly from A -> C

As you might imagine, some segments are curvy, some are straight. The straight ones aren't super exciting to plot. Below are 2 particularly curvy segments. The one on the left is a much longer road bike segment than the mountain bike segment on the right. As you can see by the curvy1 and curvy2 metrics, there is quite the different scale, but the curvier segment shows an increased curvy1 and curvy2.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/segment_polyline_maps2.png)
* A couple of fun segments recreated from their polylines.*


Prior to modeling, features were tested for their individual significance vs. the target. Many features looked at had had a P-value near 0, indicating statistical significance for any reasonable threshold. The t-statistic is an indicator of the relative impact of that feature on the target.

| Feature         | t-statistic| p-value  |
| --------------- |:---------:| --------:|
|distance: 	 	    |12.29  	  |1.47E-34  |
|average_grade: 	|38.32  	  |4.70E-309 |
|elevation_low: 	|-29.34 	  |6.00E-185 |
|elapsed_time:    |-16.79 	  |8.44E-63  |
|avge_heartrate: 	|9.20 	    |3.83E-20  |
|curvy1: 	 	      |-86.77 	  |0.00E+00  |
|curvy2: 	 	      |-83.15 	  |0.00E+00  |

Select features are shown in boxplots below:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/boxplots.png)
*Boxplots of select features. Clear separation is seen on the right 3 metrics. Interestingly, even though there's considerable overlap in the groupings of average_heartrate, it still has a tiny P-value*


Data was split into train and test groups, and several combinations of variables were tested: 
* **curvy2** was chosen over curvy1. While they performed similarly, curvy2 has more interpretable units than curvy2. Also curvy2 is much less computationaly intensive.
* **elevation_low** was used along with **average_grade** to convey the amount of climbing or descending. I could have used elevation_low and elevation_high, but would've need to use the sign of grade to transform them into something like elevation_start and elevation_finish.
* Ultimately, distance and elapsed_time were abandonded in favor of **average_speed** in order to reduce somewhat colinear features and simplify the mode.
* average_heartrate was tried and later dropped. It had the lowest feature importance and also had a lot of missing values as I don't wear my heart rate monitor on every ride. Including this feature would also limit the generalizabilty (if that wasn't a word, it is now) of the model.

#### Modeling

Several classification models types were tested including logistic regression, kNN, and naive Bayes. A rather vanilla random forest model with 100 regressors was found to yield excellent performance with about 99% accuracy, precision, and recall. A random forest is a collection of decision trees where a subset of features to be used at each split are chosen (like the name says) at random. An ensemble of trees is grown and the results averaged to get the final model. An example, rather stumpy tree is shown below. This may or may not have been the start of any of the trees grown in the forest and is for illustrative purposes only.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/decision_tree.png)</br>
*Example decision tree*


I tried tweaking the meta-parameters such as the max tree depth, number of features, etc, but any increase in model perfomance seemed to have as much to do with a random trial than any particular feature, with accuracy bouncing around 98%-99%.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/rf_confusion_matrix.png)</br>
*Confusion matrix of the ultimate model. Absolute counts are on the left and normalized percentages on the right.*


All the trials were tested throughout a range of thresholds for the classifier. I also liked this model because the best performance resulted from a threshold near 50%, which, for whatever reason, is more aesthetically pleasing to me.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/rf_model_peformance.png)</br>
*Random Forest model performance vs. threshold set for the final model*


The most important feature was found to be curvy-ness, which is reassuring as it was the feature which took the longest to engineer. The feature importances are relatively well balanced over the 4 features used.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/classification_feature_importance.png)</br>
*Feature importances for final model*

Feature ranking:
1. curvy2 (37.4%)
2. avg_speed (23.2%)
3. average_grade (22.9%)
4. elevation_low (16.6%)


## How Long Will It Take? - Regression Modeling

#### Getting the data 

For the second part of this project, I wanted to be able to estimate segment times for segments I'd never ridden before. Of course, in order to test my model, I'd need to look at segments I *had* ridden before, but given additional data, it is generalizable from here.

Beyond the best efforts of the top 10 riders on a segment, Strava does not provide segment times through its API. I initially looked at splitting my data into two groups. Though I first considered random sampling, I thought it would be best if I got max separation by splitting the the data from each segment into slow Scott/fast Scott groupings. 

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/enchanted_forest_histogram.png)</br>
*Histograms of my times on a trail called "Enchanted Forest." Not to be confused with a random forest.*

The problem with this method is that it would result in two sets of data that are decidely non-normally distributed. Though I thought I could bootstrap my way out of this problem (i.e. sample each half of the distribution with replacement in order ot get a normally distributed data set), the simpler, and actually more relevant approach, was to download K's data and predict her times based on mine.

#### Test/train split

There's one more bit of trickiness before getting on to the modeling: when splitting the data into test and train sets, I couldn't use a standard test/train split, since it would be splitting on each segment effort rather than segment itself, giving considerable data leakage and resulting in a highly overfit model.

To get around this issue, I created groups by segment, rather than random rows. So no efforts from segments in the test set were used in the training set.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/splitting.png)
*Splitting the data set. In this example, elapsed_time is an X and mean_k is the y. The left split would not be in regards to segment_id and the target, mean_k. The right splits on segment_id and does not pollute the train with test data. Note, in reality there are more than two segments to model.*

#### Feature selection

Using my experinece from the classification stufy above, I selected mostly the same features. However, in this case I did use distance and ellapsed_time instead of average_speed because time is what i was tyring to predict. Not using my ellapsed time to predict K's elapsed time proved to be a folly.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/feature_correlations.png)</br>
*Correlations of thefeatures that were used in this model. mean_k is the target average time to be predicted. Note the high correlation with ellapsed time. (That's called foreshadowing, folks)*

In the end, I used **ellapsed_time**, **distance**, **average_grade**, and **curvy2**.

#### Model performance

Again, of the models attempted, random forest came out on top with an R-squared of 0.97, meaning the model predicted about 97% of the variation seen in the data. Also the RMSE of 197 is easily interpreted as one could expect K's actual average time to be +/- 3 minutes or so from the predicted time. While this is a lousy range for really short segments, it's very good for long segments (the longest in this set being over 3 hours), where this functionality is most useful anyway.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/rf_regressor_performance.png)</br>
*Actual times vs. random forest predicted times.*

What's not so exciting about this model is that the most important feature, by far, is my ellapsed_time. In contrast to the relatively balanced features of the clarrification mode able, the other features of segment characteristics are much less signficant.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/regression_feature_importance.png)</br>
*Feature importance of model*

While this isn't necessarily surpising, it's a bit demorilizing that I can get nearly the same performance by simply making a single variable linear fit to my times vs. K's times to predict her time on other segments with >80% accuracy.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/linear_fit.png)</br>
*If I didn't know all this data science stuff, this would be the best I'd go on to predict times. The slope says that in order to estimate her average time on any segment, just take my average time and multiply by ~1.2* 

## Further work

Especially with other apps such as [Trailforks](https://www.trailforks.com) and [MTB Project](https://www.mtbproject.com), **Which Bike Should I Bring?** was largely a passion project/academic exercise just to see if I could do it. With only having my labeled data and using my average speed as a feature, it's currently specific to trails I've ridden. However, I could extend to any segment by using average speeds calculated from the top 10 times of the Strava leaderboard, which is accessible via the API. Another extension of this dataset could be to use some unsupervised modeling on mountain bike segments in order to objectively classify them with the goal of perhaps being able to distiguish technical difficulty.

In contrast, given access to the full database, **How Long Will It Take?** could be extended for any number of Strava users. On any particular segment, you would only need to find one user in common that you've done the same segment as in order to estimate your time. Taking it a bit further, one could imagine a tool that uses higher order connections (a'la [Six Degrees of Kevin Bacon](https://oracleofbacon.org)) to estimate your time on any segment.

Lastly, while **How Long Will It Take?** is currently implemented with your average time, you could easily modify it to estimate your best time, or 90th percentile time, or whatever you want in order to figure out a good "challenge time" for yourself.
