nomenklatura.controller('UploadCtrl', ['$scope', '$routeParams', '$modalInstance', '$location', '$http', '$sce', 'session', 'dataset',
  function ($scope, $routeParams, $modalInstance, $location, $http, $sce, session, dataset) {
  $scope.dataset = angular.copy(dataset);
  $scope.form_action = '/api/2';
  $scope.upload = {};

  $scope.$watch('dataset', function() {
    $scope.form_action = $sce.trustAsResourceUrl('/api/2/datasets/' + $scope.dataset.name + '/uploads');
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.results = function(content) {
    if (!content.parse_error) {
      $modalInstance.dismiss('cancel');
      $location.path('/datasets/' + $scope.dataset.name + '/uploads/' + content.id);
    } else {
      $scope.upload = content;
    }
  };
}]);


var loadUpload = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      params = $route.current.params;
  var url = '/api/2/datasets/' + params.dataset + '/uploads/' + params.upload;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('MappingCtrl', ['$scope', '$routeParams', '$location', '$http', 'session', 'dataset', 'upload',
  function ($scope, $routeParams, $location, $http, session, dataset, upload) {

  $scope.errors = {};
  $scope.dataset = dataset;
  $scope.upload = upload;
  $scope.mapping = {'columns': {}, 'reviewed': true};

  $scope.beginImport = function() {
    var dfd = $http.post(upload.api_url, $scope.mapping);
    dfd.success(function(res) {
      $location.path('/datasets/' + $scope.dataset.name);
    });
    dfd.error(function(res) {
      $scope.errors = res;
    });
  };
}]);
