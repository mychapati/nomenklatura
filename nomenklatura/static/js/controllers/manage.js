
nomenklatura.controller('ManageCtrl', ['$scope', '$routeParams', '$modal', '$location', '$http', '$sce', 'imports', 'users',
  function ($scope, $routeParams, $modal, $location, $http, $sce, imports, users) {

  $scope.imports = imports;
  $scope.users = users;

  $scope.upload = function(){
    var d = $modal.open({
      templateUrl: '/static/templates/imports/upload.html',
      controller: 'ImportsUploadCtrl',
      resolve: {}
    });
  };

  $scope.roleChange = function(user) {
    $http.post(user.api_url, user);
  };

  $scope.readonlyRole = function(user) {
    return user.id == $scope.session.user.id;
  };

}]);
