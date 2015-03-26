function AppCtrl($scope, $window, $routeParams, $location, $modal, Session, Flash) {
    $scope.session = {logged_in: false};
    $scope.flash = Flash;

    Session.get(function(data) {
        $scope.session = data;
    });

    $scope.keyDownNotify = function($event) {
        if(angular.lowercase($event.target.tagName) == 'body') {
            $scope.$broadcast('key-pressed', $event.keyCode);
        }
    };

    $scope.showProfile = function() {
        var d = $modal.open({
            templateUrl: '/static/templates/users/profile.html',
            controller: 'ProfileCtrl'
        });
    };
}

AppCtrl.$inject = ['$scope', '$window', '$routeParams', '$location', '$modal', 'Session', 'Flash'];
