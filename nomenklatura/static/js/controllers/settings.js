var loadRoleUsers = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();

  Session.get(function(s) {
    var params = {params: {_uid: s.cbq}};
    $http.get('/api/2/users', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });

  return dfd.promise;
}];


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
