# Creating New Functionality for Strava

## Introduction

![](https://www.ride25.com/wp-content/uploads/2014/10/strava_rgb_logotype.png "Strava Logo")

[Strava](https://www.strava.com) is an app at the juxtiposition of social networking, fitness, and GPS tracking. Used mostly by cyclists and runners, Strava allows athletes can upload GPS tracks of their workouts to share with their friends (and the rest of the internet). The unique feature Strava has is user-defined "segments" which function as short, virtual racecourses where an athelete can compare times against themselves to try to get a PR (personal record), and others for the course record (also known as the K/QOM -- King/Queen of the Mountain for cycling).

I've used Strava for many years mostly as a cyclist. In addition to using it for ride tracking and competition (even if only in my head), I've also used it to find new places to ride and estimate how long a ride will take me. 

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

Many segements are rather short, a mile or less, but some map out an entire ride.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/buffalo_brain_loop.png) <br/>
*[The Buffalo Brain Loop](https://www.strava.com/segments/2490347) is almost a complete ride*

Had I never ridden this before, it would be nice to know how long it will take me to complete this ride. Or, alternatively, what's a good time with which to challenge myself with? Strava allows to view the "leaderboard" and see everyone's best time on a given segment. And it even allows you to filter down to atheletes you are following. But still, how do I know how an average time of mine will compare to any one other rider's best time? Accordingly, I've developed a model that will estimate your time on a segment you haven't ridden in comparison to a rider you have ridden with before

## Data collection

Strava has an [API](http://developers.strava.com) which, in a very "there's an app for that" moment, can be accessed with the [stravalib](https://pythonhosted.org/stravalib/) library. Setting up a Flask site to use the API is isn't that hard, but it's not that easy, either. [hozn's Github repo](https://github.com/hozn/stravalib) provides a good walkthrough on how to do this. Unfortunately, the rates you can pull data are throttled significantly, and the data you can gather is limited to users who have password authorized your app. 

Fortunately, I have recorded a couple thousand myself and my wife has hundreds more, so this provided the fodder I needed for the modeling done below.

[get_strava_data.py]https://github.com/scottfeldmanpeabody/strava/blob/master/src/get_strava_data.py creates a StravaAthlete class and allows you to download data for that athlete. It also creates a directory structure to store the data in /strava/data/user_name/ once you've created the /strava directory.

## Which Bike Should I Bring? - Categorical Modeling

Firstly, there are far too many categories of bikes these days (see [wikipedia](https://en.wikipedia.org/wiki/List_of_bicycle_types) for what's still probably an incomplete list), but for an average Strava user, it breaks down to road bike or mountain bike.

In order to determine whether a segment is a road bike or a mountain bike segment, I was able to use the features that Strava lets you label each ride with the bike you rode. 

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/attempts_by_bike.png)</br>
*Count of Strava segments ridden on each bike. Note, there are sometimes dozens of segments per ride, hence the large y scale*

So it's obvious to the  that "Road", "Carbon Road", and "Road + Burley" (a Burley is a kid trailer), are all road bikes, I was able to sort out my more creative bike names and group them into the two categories of interest. It turns out it's rather well balanced by segment attempts without me doing anything:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/attempts_by_bike_type.png)</br>
*This data set is balanced AF*

For each segment, Strava provides a number of features, not all of which are independent of each other. For instance, between
* Distance
* Elevation Low
* Elevation High
* Average Grade
There are only really 3 independent variables.

For each segment attempt (a.k.a. effort), I also have a time. I calculated an average speed for each effort using (segment distance)/(effort time). For many efforts I have both an average and max heart rate. The max heart rate tends to be bogus most of the time due to errors from the heart rate monitor. 

Another piece of data you can get from Strava is the google polyline for the segment. As with the Strava API, [there's library for that](https://pypi.org/project/polyline/). A google polyline is a string that can be decoded into a list of (latitude, longitude) tuples with polyline.decode(). These points can then be plotted to give a map of the entire segment. I used each series of 3 points to get a "curviness" metric out of the polyline. An example of three points is shown below:

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/defining_curvy.png)</br>
*Diagram for defining curvy metrics from the polyline. Segments AB and BC are consecutive points on the map. AC is a construction used in the definition of curvy2 (def. below).*

Two metrics for curviness were developed as curvy1() and curvy2() in the [features.py](https://github.com/scottfeldmanpeabody/strava/blob/master/src/features.py) script.
1. **curvy1:** uses the cosine difference between AB and BC, then normalizes by the total length AB + length BC. The normalization is due to not all polyline segments being the same length.
2. **curvy2:** uses the ratio (length AB + length BC - length AC) / (length AB + length BC). This metric is unitless and can be viewed as a percent further distance that you traveled along the path A -> B -> C rather than had you gone directly from A -> C

As you might imagine, some segments are curvy, some are straight. The straight ones are super exciting to plot. Below are 2 particularly curvy segments. The one on the left is a much longer road bike segment than the mountain bike segment on the right. As you can see by the curvy1 and curvy2 metrics, there is quite the different scale, but the curvier segment shows an increased curvy1 and curvy2.

![](https://github.com/scottfeldmanpeabody/strava/blob/master/images/segment_polyline_maps.png)

## How Long Will It Take? - Regression Modeling

## Further work

Especially with other apps such as [Trailforks](https://www.trailforks.com) and [MTB Project](https://www.mtbproject.com), **Which Bike Should I Bring?** was largely an academic exercise. However, given access to the full database, **How Long Will It Take?** could be extended for any number of Strava users. On any particular segment, you would only need to find one user in common that you've done the same segment as in order to estimate your time. Taking it a bit further, one could imagine a tool that uses higher order connections (a'la [Six Degrees of Kevin Bacon](https://oracleofbacon.org)) to estimate your time on any segment.

Furthermore, while **How Long Will It Take?** is currently implemented with your average time, you could easily modify it to estimate your best time, or 90th percentile time, or whatever you want in order to figure out a good "challenge time" for yourself.
