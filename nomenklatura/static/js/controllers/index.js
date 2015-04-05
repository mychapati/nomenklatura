
nomenklatura.controller('IndexCtrl', ['$scope', '$location', '$http', '$modal', 'Flash', 'Meta', 'entities',
  function ($scope, $location, $http, $modal, Flash, Meta, entities) {
  var filterTimeout = null;

  $scope.schema = Meta.schema;
  $scope.entities = entities;
  $scope.new_entity = {'type': 'Person'};
  $scope.query = '';

  $scope.loadEntities = function(url, params) {
    $http.get(url, {params: params}).then(function(res) {
      $scope.entities = res.data;
    });
  };

  $scope.updateFilter = function() {
    if (filterTimeout) { $timeout.cancel(filterTimeout); }

    filterTimeout = $timeout(function() {
      var fparams = {prefix: $scope.query};
      $scope.loadEntities('/api/2/entities', fparams);
    }, 500);
  };

  $scope.createEntity = function(form) {
    var res = $http.post('/api/2/entities', $scope.new_entity);
    res.success(function(data) {
      $location.path('/entities/' + data.id);
    });
    res.error(Validation.handle(form));
  };

}]);

