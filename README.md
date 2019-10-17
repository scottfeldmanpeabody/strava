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

## Which Bike Should I Bring?

## UseHow Long Will It Take?

## Further work

Especially with other apps such as [Trailforks](https://www.trailforks.com) and [MTB Project](https://www.mtbproject.com), **Which Bike Should I Bring?** was largely an academic exercise. However, given access to the full database, **How Long Will It Take?** could be extended for any number of Strava users. On any particular segment, you would only need to find one user in common that you've done the same segment as in order to estimate your time. Taking it a bit further, one could imagine a tool that uses higher order connections (a'la [Six Degrees of Kevin Bacon](https://oracleofbacon.org)) to estimate your time on any segment.

Furthermore, while **How Long Will It Take?** is currently implemented with your average time, you could easily modify it to estimate your best time, or 90th percentile time, or whatever you want in order to figure out a good "challenge time" for yourself.
