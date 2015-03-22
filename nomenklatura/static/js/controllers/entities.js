
var loadEntity = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer();
  $http.get('/api/2/entities/' + $route.current.params.id).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];

nomenklatura.controller('EntitiesViewCtrl', ['$scope', '$routeParams', '$location',
            '$http', '$modal', '$timeout', 'dataset', 'entity',
  function ($scope, $routeParams, $location, $http, $modal, $timeout, dataset, entity) {
  $scope.dataset = dataset;
  $scope.entity = entity;
  $scope.has_attributes = entity.attributes && Object.keys(entity.attributes).length > 0;
  $scope.aliases = {};
  $scope.has_aliases = false;
  
  function loadAliases(url) {
    $http.get(url).then(function(res) {
      $scope.aliases = res.data;
      $scope.has_aliases = res.data.total > 0;
    });
  }

  loadAliases('/api/2/entities/' + $routeParams.id + '/aliases');
}]);
