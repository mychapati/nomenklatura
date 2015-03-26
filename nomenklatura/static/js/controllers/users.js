
nomenklatura.controller('UsersProfileCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Validation', 'Session',
  function ($scope, $location, $modalInstance, $http, Validation, Session) {

  $scope.session = {logged_in: false};
  $scope.user = {}

  Session.get(function(data) {
    $scope.session = data;
    $scope.user = data.user;
  });

  $scope.passwordMismatch = function() {
    return $scope.user.password && $scope.user.password != $scope.user.passwordRepeat;
  };

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
    res.error(Validation.handle(form));
  };
}]);


nomenklatura.controller('UsersResetCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Validation',
  function ($scope, $location, $modalInstance, $http, Validation) {
  $scope.data = {};

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.reset = function(form) {
    var res = $http.post('/api/2/users/reset', $scope.data);
    res.success(function(data) {
      $modalInstance.dismiss('ok');
    });
    res.error(Validation.handle(form));
  };
}]);


nomenklatura.controller('UsersLoginCtrl', ['$scope', '$location', '$modal', '$http', '$window', 'Validation', 'Session', 'Flash',
  function ($scope, $location, $modal, $http, $window, Validation, Session, Flash) {

  $scope.session = {logged_in: false};
  $scope.newUser = {};
  $scope.loginData = {};
  $scope.registerForm = {};

  Session.get(function(data) {
    $scope.session = data;
  });

  $scope.openReset = function() {
    var d = $modal.open({
      templateUrl: '/static/templates/users/reset.html',
      controller: 'UsersResetCtrl'
    });
  };

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
    $scope.newUser.password = '';
    $scope.newUser.passwordRepeat = '';
    res.success(function(data) {
      $location.path('/');
      var message = 'You will receive a confirmation email with an activation link.';
      Flash.message('Thank you for registering. ' + message, 'success');
    });
    res.error(Validation.handle(form));
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
      $location.path('/');
      $window.location.reload(true);
    });
    res.error(Validation.handle(form));
  };

}]);
