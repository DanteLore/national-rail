var mapApp = angular.module('mapApp', ['ngRoute']);

// Map tiles from: http://leaflet-extras.github.io/leaflet-providers/preview/index.html CartoDB.DarkMatter

mapApp
    .config(function($routeProvider){
	    $routeProvider
		    .when('/',
		    {
		    	controller: 'MapController',
			    templateUrl: 'map.html'
		    })
		    .otherwise({redirectTo: '/'});
	})
	.controller('MapController', function($scope, $http, $timeout, $routeParams) {

        var mymap = L.map('mapid').fitBounds([ [51.3933180851, -1.24174419711], [51.5154681995, -0.174688620494] ]);

        var CartoDB_DarkMatter = L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
            subdomains: 'abcd',
            maxZoom: 19
        });

        CartoDB_DarkMatter.addTo(mymap);

        $http.get("/routes/PAD").success(function(data) {
            data.forEach(function(route){
                route.forEach(function(station) {
                    var location = [station.latitude, station.longitude]

                    L.circle(location, 50, {
                        color: 'yellow',
                        fillColor: 'yellow',
                        fillOpacity: 0.5
                    }).addTo(mymap);

                    //L.marker(location).addTo(mymap);
                });
            });
        });
    });