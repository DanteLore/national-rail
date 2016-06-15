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

        var categoryScale = d3.scale.category10();

        $scope.doStation = function(data) {
            data.forEach(function(route){
                var color = categoryScale(route[0].crs)
                var path = []

                route.filter(function(x) {return x.latitude && x.longitude}).forEach(function(station) {
                    var location = [station.latitude, station.longitude];
                    path.push(location);

                    L.circleMarker(location, {
                        radius: 3,
                        color: "black",
                        weight: 1,
                        stroke: true,
                        fillColor: color,
                        fillOpacity: 1
                    }).addTo(mymap);

                    //L.marker(location).addTo(mymap);
                });

                L.polyline(path, {
                    weight: 2,
                    color: color
                }).addTo(mymap);
            });
        };

        $http.get("/routes/CHX").success($scope.doStation);
        $http.get("/routes/MYB").success($scope.doStation);
        $http.get("/routes/EUS").success($scope.doStation);
        $http.get("/routes/STP").success($scope.doStation);
        $http.get("/routes/WAT").success($scope.doStation);
        $http.get("/routes/KGX").success($scope.doStation);
        $http.get("/routes/LST").success($scope.doStation);
        $http.get("/routes/PAD").success($scope.doStation);
    });