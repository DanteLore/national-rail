var departuresApp = angular.module('departuresApp', ['ngRoute']);

departuresApp
    .config(function($routeProvider){
	    $routeProvider
		    .when('/:crs',
		    {
		    	controller: 'DeparturesController',
			    templateUrl: 'board.html'
		    })
		    .otherwise({redirectTo: '/THA'});
	})
	.controller('DeparturesController', function($scope, $http, $timeout, $routeParams) {

        $scope.crs = $routeParams.crs

        $scope.tick = function() {
            function checkTime(i) {
                if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
                return i;
            }

            var today = new Date();
            var h = today.getHours();
            var m = today.getMinutes();
            var s = today.getSeconds();
            m = checkTime(m);
            s = checkTime(s);

            $scope.clock = h + ":" + m + ":" + s;

            $timeout(function(){
                $scope.tick();
            }, 1000)
        }

        $scope.refreshTrains = function() {
            $http.get("/departures/" + $scope.crs).success(function(data) {
                $scope.trains = data;
            });

            $timeout(function(){
                $scope.refreshTrains();
            }, 10000)
        };

        $scope.refreshTrains();
        $scope.tick();


    });