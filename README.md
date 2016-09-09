# National Rail

There are many parts to this repo, doing simple things with the National Rail SOAP API. Feel free to use bits and bobs as it suits you, with attribution of course!

* A script to tweet live train information can be found in "tweetrail"
* Scripts to collect and store data are in "collectors"
* An AngularJS departure board can be found in "ui/departure-board"
* A map app showing live routing animations can be found in "ui/route-map"

Learn more about the code on my website and/or follow either the [Thatcham Train Twitter Feed](https://twitter.com/ThatchamTrains) or [me (DanteLore)](https://twitter.com/DanteLore) on twitter:

* [Thatcham Trains: The National Rail and Twitter Mash-Up](http://logicalgenetics.com/thatcham-trains/)
* [Live Train Route Animation](http://logicalgenetics.com/live-train-route-animation/)
* [Live Train Departure Board](http://logicalgenetics.com/train-departure-board/)

![Live Route Display](http://logicalgenetics.com/wp-content/uploads/2016/06/route-planner.gif)

![Live Departures](http://logicalgenetics.com/wp-content/uploads/2016/06/departures-1024x758.png)

Enjoy!




## Installing under lighttpd

Clone this repo to your web root and edit some config files for lighttpd.

Add the following to /etc/lighttpd/conf.d/fastcgi.conf (or /usr/local/etc/lighttpd/conf.d/fastcgi.conf if you're on a Mac)

```
fastcgi.server = (
    "rail.fcgi" => ((
        "socket" => "/tmp/rail-fcgi.sock",
        "bin-path" => "/usr/local/var/www/national-rail/rail.fcgi",
        "check-local" => "disable",
        "max-procs" => 1
    ))
)
```

And make sure you have FastCGI enabled in /etc/lighttpd/modules.conf