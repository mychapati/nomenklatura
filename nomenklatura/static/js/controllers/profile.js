function ProfileCtrl($scope, $location, $modalInstance, $http, session) {
  $scope.session = {logged_in: false};
  $scope.user = {}

  session.get(function(data) {
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
  };  
    
}

ProfileCtrl.$inject = ['$scope', '$location', '$modalInstance', '$http', 'session'];
