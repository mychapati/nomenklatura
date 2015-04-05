
nomenklatura.controller('SettingsCtrl', ['$scope', '$route', '$routeParams', '$location', '$http', 'Validation', 'users',
  function ($scope, $route, $routeParams, $location, $http, Validation, users) {
  $scope.users = users;

  $scope.roleChange = function(user) {
    $http.post(user.api_url, user);
  };

  $scope.readonlyRole = function(user) {
    return user.id == $scope.session.user.id;
  };

}]);
