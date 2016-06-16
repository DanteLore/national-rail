var mapApp = angular.module('mapApp', ['ngRoute']);

// Map tiles from: http://leaflet-extras.github.io/leaflet-providers/preview/index.html CartoDB.DarkMatter

// _Awesome_ snake from: https://github.com/IvanSanchez/Leaflet.Polyline.SnakeAnim

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
        }).addTo(mymap);

        $scope.routeLayer = L.featureGroup()
            .addTo(mymap);

        $scope.categoryScale = d3.scale.category10();

        $scope.doStation = function(data) {
            data.forEach(function(route){
                var color = $scope.categoryScale(route[0].crs)
                var path = Array()

                route.filter(function(x) {return x.latitude && x.longitude}).forEach(function(station) {
                    var location = [station.latitude, station.longitude];
                    path.push(location);
                });

                var line = L.polyline(path, {
                    weight: 4,
                    color: color,
                    opacity: 0.5
                }).addTo($scope.routeLayer);

                try {
                    if(path.length > 1)
                        line.snakeIn();
                }
                catch (e) {
                    console.log("Error: " + path)
                }
            });
        };

        $scope.refresh = function() {
            $scope.routeLayer.clearLayers();

            $scope.crsList.forEach(function(crs) {
                $http.get("/routes/" + crs).success($scope.doStation);
            });

            $timeout(function(){
                $scope.refresh();
            }, 10000)
        };

        $http.get("/loaded-crs").success(function(crsData) {
            $scope.crsList = crsData;

            $scope.refresh();
        })
    });