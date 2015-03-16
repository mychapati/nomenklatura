
var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer();
  $http.get('/api/2/datasets/' + $route.current.params.dataset).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadDatasetEntities = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      params = {
        dataset: $route.current.params.dataset
      };
  $http.get('/api/2/entities', {params: params}).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('DatasetsViewCtrl', ['$scope', '$routeParams', '$location', '$http', '$modal',
                                             '$timeout', 'session', 'dataset', 'entities',
    function ($scope, $routeParams, $location, $http, $modal, $timeout, session, dataset, entities) {

    $scope.dataset = dataset;
    $scope.entities = entities;
    $scope.new_entity = {};
    $scope.query = '';

    $scope.aliases_percent = Math.ceil((dataset.stats.num_aliases / dataset.stats.num_entities)*100);
    $scope.invalid_percent = Math.ceil((dataset.stats.num_invalid / dataset.stats.num_entities)*100);
    $scope.review_percent = Math.ceil((dataset.stats.num_review / dataset.stats.num_entities)*100);
    $scope.normal_percent = 100 - $scope.aliases_percent - $scope.invalid_percent - $scope.review_percent;
    $scope.normal_num = dataset.stats.num_entities - dataset.stats.num_aliases -
        dataset.stats.num_invalid - dataset.stats.num_review;

    $scope.loadEntities = function(url, params) {
        $http.get(url, {params: params}).then(function(res) {
            $scope.entities = res.data;
        });
    };

    var filterTimeout = null;

    $scope.updateFilter = function() {
        if (filterTimeout) { $timeout.cancel(filterTimeout); }

        filterTimeout = $timeout(function() {
            var fparams = {
              dataset: dataset.name,
              filter_name: $scope.query
            };
            $scope.loadEntities('/api/2/entities', fparams);
        }, 500);
    };

    $scope.editDataset = function() {
        var d = $modal.open({
            templateUrl: '/static/templates/datasets/edit.html',
            controller: 'DatasetsEditCtrl',
            resolve: {
                dataset: function () { return $scope.dataset; }
            }
        });
    };

    $scope.uploadFile = function(){
        var d = $modal.open({
            templateUrl: '/static/templates/upload.html',
            controller: 'UploadCtrl',
            resolve: {
                dataset: function () { return $scope.dataset; }
            }
        });
    };

    $scope.createEntity = function(form) {
        $scope.new_entity.dataset = $scope.dataset.name;
        $scope.new_entity.attributes = {};
        var res = $http.post('/api/2/entities', $scope.new_entity);
        res.success(function(data) {
            $location.path('/entities/' + data.id);
        });
        res.error(nomenklatura.handleFormError(form));
    };
}]);


nomenklatura.controller('DatasetsNewCtrl', ['$scope', '$routeParams', '$modalInstance', '$location', '$http', 'session',
  function ($scope, $routeParams, $modalInstance, $location, $http, session) {
  $scope.dataset = {};

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.create = function(form) {
    var res = $http.post('/api/2/datasets', $scope.dataset);
    res.success(function(data) {
      $location.path('/datasets/' + data.name);
      $modalInstance.dismiss('ok');
    });
    res.error(nomenklatura.handleFormError(form));
  };
}]);


nomenklatura.controller('DatasetsEditCtrl', ['$scope', '$route', '$routeParams', '$modalInstance', '$location', '$http', 'dataset',
  function ($scope, $route, $routeParams, $modalInstance, $location, $http, dataset) {
  $scope.dataset = angular.copy(dataset);

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.update = function(form) {
    var res = $http.post('/api/2/datasets/' + $scope.dataset.name, $scope.dataset);
    res.success(function(data) {
      $route.reload();
      $modalInstance.dismiss('ok');
    });
    res.error(nomenklatura.handleFormError(form));
  };
}]);
