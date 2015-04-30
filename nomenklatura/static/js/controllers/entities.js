
var loadEntity = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/2/entities/' + $route.current.params.id;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('EntitiesViewCtrl', ['$scope', '$routeParams', '$location',
            '$http', '$modal', '$timeout', 'Meta', 'entity',
  function ($scope, $routeParams, $location, $http, $modal, $timeout, Meta, entity) {

  $scope.entity = entity;
  $scope.schema = Meta.schema;
  $scope.editing = false;

  $scope.beginEdit = function(){
    $scope.editedEntity = angular.copy($scope.entity);
    $scope.editing = true;
  };

  $scope.saveEdit = function(){
    $scope.editing = false;
    $scope.entity = $scope.editedEntity;

    $http.post($scope.entity.api_url, $scope.entity).
    success(function(data, status, headers, config) {
      $scope.editedEntity = null;
    }).
    error(function(data, status, headers, config) {
      // display message to user
    });

    // spinny thing
    // why not put?
    // make save a factory service

  };

  $scope.cancelEdit = function(){
    $scope.editing = false;
    $scope.editedEntity = null;
  };

}]);

