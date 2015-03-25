
nomenklatura.controller('UploadCtrl', ['$scope', '$routeParams', '$modalInstance', '$location',
                                       '$http', '$sce', 'dataset',
  function ($scope, $routeParams, $modalInstance, $location, $http, $sce, dataset) {
  $scope.dataset = dataset;
  $scope.form_action = '/api/2';
  $scope.upload = {};

  $scope.$watch('dataset', function() {
    $scope.form_action = $sce.trustAsResourceUrl('/api/2/datasets/' + $scope.dataset.slug + '/imports');
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.results = function(content) {
    if (!content.parse_error) {
      $modalInstance.dismiss('cancel');
      $location.path('/datasets/' + $scope.dataset.slug + '/imports/' + content.id);
    } else {
      $scope.upload = content;
    }
  };
}]);


var loadUpload = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      params = $route.current.params;
  var url = '/api/2/datasets/' + params.dataset + '/imports/' + params.context;
  $http.get(url).then(function(res) {
    res.data.api_url = url;
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('ImportsMappingCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$q', '$http', 'dataset', 'upload', 'schema',
  function ($scope, $routeParams, $location, $timeout, $q, $http, dataset, upload, schema) {

  var uploadCheck = null, importStarted = false;
  $scope.hasTable = false;
  $scope.schema = schema;
  $scope.dataset = dataset;
  $scope.upload = upload;
  $scope.context = upload.context;
  $scope.mapping = upload.mapping;

  var checkAnalysis = function() {
    if ($scope.upload.table && $scope.upload.table.fields) {
      return $scope.hasTable = true;
    }
    uploadCheck = $timeout(function() {
      var dt = new Date(),
          config = {params: {'_': dt.getTime()}, ignoreLoadingBar: true};
      $http.get(upload.api_url, config).then(function(res) {
        $scope.upload.table = res.data.table;
        checkAnalysis();
      });
    }, 1000);
  };

  $scope.$on("$destroy", function() {
    $timeout.cancel(uploadCheck);
  });

  checkAnalysis();

  $scope.canImport = function() {
    return $scope.hasTable && !importStarted && upload.context_statements <= 0;
  }

  $scope.save = function(form) {
    var dfd = $q.defer(),
        data = angular.copy($scope.context);
    
    data.resource_mapping = $scope.mapping;
    var res = $http.post(data.api_url, data);
    res.success(function(data) {
      $scope.context = data;
      dfd.resolve();
    });
    res.error(nomenklatura.handleFormError(form));
    return dfd.promise;
  }

  $scope.import = function(form) {
    if (!$scope.canImport()) {
      return;
    }
    $scope.save(form).then(function() {
      importStarted = true;
      var dfd = $http.post(upload.api_url);
      dfd.success(function(res) {
        $location.path('/datasets/' + $scope.dataset.slug + '/imports/' + upload.context.id + '/status');
      });
      dfd.error(function(res) {
        $scope.errors = res;
        importStarted = false;
      });  
    });
  };
}]);


nomenklatura.controller('ImportsStatusCtrl', ['$scope', '$routeParams', '$location', '$interval', '$q', '$http', 'dataset', 'upload',
  function ($scope, $routeParams, $location, $interval, $q, $http, dataset, upload) {

  var url = '/api/2/datasets/' + dataset.slug + '/imports/' + upload.context.id + '/logs';
  $scope.dataset = dataset;
  $scope.upload = upload;
  $scope.logs = {};

  var stopInterval = $interval(function() {
    $http.get(url).then(function(res) {
      $scope.logs = res.data;
    })
  }, 1000);

  $scope.$on('$destroy', function() {
    $interval.cancel(stopInterval);
  });

}]);
