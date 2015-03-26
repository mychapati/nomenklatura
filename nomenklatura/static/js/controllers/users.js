
nomenklatura.controller('ProfileCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session',
  function ($scope, $location, $modalInstance, $http, Session) {

  $scope.session = {logged_in: false};
  $scope.user = {}

  Session.get(function(data) {
    $scope.session = data;
    $scope.user = data.user;
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.update = function(form) {
    var res = $http.post($scope.user.api_url, $scope.user);
    res.success(function(data) {
      $scope.user = data;
      $scope.session.user = data;
      $modalInstance.dismiss('ok');
    });
    res.error(nomenklatura.handleFormError(form));
  };
}]);



nomenklatura.controller('LoginCtrl', ['$scope', '$location', '$modal', '$http', 'Session',
  function ($scope, $location, $modal, $http, Session) {

  $scope.session = {logged_in: false};
  $scope.newUser = {};
  $scope.loginData = {};
  $scope.registerForm = {};

  Session.get(function(data) {
    $scope.session = data;
  });

  $scope.passwordMismatch = function() {
    return $scope.newUser.password != $scope.newUser.passwordRepeat;
  };

  $scope.canRegister = function() {
    return $scope.newUser.password && $scope.newUser.password.length > 2 &&
      !$scope.passwordMismatch() && 
      $scope.newUser.display_name && $scope.newUser.display_name.length > 2 &&
      $scope.newUser.email && $scope.newUser.email.length > 2;
  };

  $scope.register = function(form) {
    if (!$scope.canRegister()) {
      return;
    }
    var res = $http.post('/api/2/users/register', $scope.newUser);
    res.success(function(data) {
      //$scope.user = data;
      //$scope.session.user = data;
      //$modalInstance.dismiss('ok');
    });
    res.error(nomenklatura.handleFormError(form));
  };

  $scope.canLogin = function() {
    return $scope.loginData.password && $scope.loginData.password.length > 2 &&
      $scope.loginData.email && $scope.loginData.email.length > 2;
  };

  $scope.login = function(form) {
    if (!$scope.canLogin()) {
      return;
    }
    var res = $http.post('/api/2/users/login', $scope.loginData);
    $scope.loginData.password = null;
    res.success(function(data) {
      //$scope.user = data;
      //$scope.session.user = data;
      //$modalInstance.dismiss('ok');
    });
    res.error(nomenklatura.handleFormError(form));
  };
}]);
