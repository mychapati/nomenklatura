nomenklatura.controller('AppCtrl', ['$scope', '$window', '$routeParams', '$location', '$modal', 'Session', 'Flash',
    function ($scope, $window, $routeParams, $location, $modal, Session, Flash) {

    $scope.session = {logged_in: false};
    $scope.flash = Flash;

    Session.get(function(data) {
        $scope.session = data;
    });

    $scope.showProfile = function() {
        var d = $modal.open({
            templateUrl: '/static/templates/users/profile.html',
            controller: 'UsersProfileCtrl'
        });
    };
}]);
