
var loadEntity = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      pa = $route.current.params,
      url = '/api/2/datasets/' + pa.dataset + '/entities/' + pa.id;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadSchema = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer();
  $http.get('/api/2/schema').then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('EntitiesViewCtrl', ['$scope', '$routeParams', '$location',
            '$http', '$modal', '$timeout', 'schema', 'dataset', 'entity',
  function ($scope, $routeParams, $location, $http, $modal, $timeout, schema, dataset, entity) {
  $scope.dataset = dataset;
  $scope.entity = entity;
  $scope.schema = schema;

}]);
