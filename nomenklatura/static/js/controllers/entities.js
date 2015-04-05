
nomenklatura.controller('EntitiesViewCtrl', ['$scope', '$routeParams', '$location',
            '$http', '$modal', '$timeout', 'Meta', 'entity',
  function ($scope, $routeParams, $location, $http, $modal, $timeout, Meta, entity) {

  $scope.entity = entity;
  $scope.schema = Meta.schema;

}]);
