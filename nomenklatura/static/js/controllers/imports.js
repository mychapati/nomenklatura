
var loadImports = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
      
  Session.get(function(s) {
    var params = {params: {_uid: s.cbq, imports: true}};
    $http.get('/api/2/contexts', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


nomenklatura.controller('ImportsIndexCtrl', ['$scope', '$routeParams', '$modal', '$location', '$http', '$sce', 'imports',
  function ($scope, $routeParams, $modal, $location, $http, $sce, imports) {
  $scope.imports = imports;

  $scope.upload = function(){
    var d = $modal.open({
      templateUrl: '/static/templates/imports/upload.html',
      controller: 'ImportsUploadCtrl',
      resolve: {}
    });
  };

}]);


nomenklatura.controller('ImportsUploadCtrl', ['$scope', '$routeParams', '$modalInstance', '$location', '$http',
  function ($scope, $routeParams, $modalInstance, $location, $http) {
  $scope.upload = {};

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.results = function(content) {
    if (!content.parse_error) {
      $modalInstance.dismiss('cancel');
      $location.path('/imports/' + content.id);
    } else {
      $scope.upload = content;
    }
  };
}]);


var loadUpload = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/2/imports/' + $route.current.params.context;
  $http.get(url).then(function(res) {
    res.data.api_url = url;
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


nomenklatura.controller('ImportsMappingCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$q', '$http', '$modal', 'Validation', 'upload', 'Meta',
  function ($scope, $routeParams, $location, $timeout, $q, $http, $modal, Validation, upload, Meta) {

  var uploadCheck = null, importStarted = false;
  $scope.schema = Meta.schema;
  $scope.upload = upload;
  $scope.context = upload.context;
  $scope.mapping = upload.mapping;
  $scope.state = null;
  $scope.logs = {};

  $scope.isAnalyzing = function() { return $scope.state == 'analyzing'; };
  $scope.isAnalyzed = function() { return $scope.state == 'analyzed'; };
  $scope.isLoading = function() { return $scope.state == 'loading'; };
  $scope.isLoaded = function() { return $scope.state == 'loaded'; };
  $scope.isFailed = function() { return $scope.state == 'failed'; };

  $scope.canImport = function() {
    return $scope.isAnalyzed() && !importStarted && upload.context_statements <= 0;
  };

  var refreshData = function() {
    var dt = new Date(),
        config = {params: {'_': dt.getTime()}, ignoreLoadingBar: true};
    $q.all([
      $http.get(upload.api_url, config),
      $http.get(upload.api_url + '/logs', config)
    ]).then(function(res) {
      $scope.upload.table = res[0].data.table;
      $scope.context.active = res[0].data.context.active;
      $scope.logs = res[1].data;
      $scope.state = res[0].data.source.state || 'analyzing';
      updateState();
    });
  };

  var updateState = function() {
    if ($scope.isAnalyzing() || $scope.isLoading()) {
      uploadCheck = $timeout(refreshData, 2000);
    }
  };

  $scope.$on("$destroy", function() {
    $timeout.cancel(uploadCheck);
  });

  $scope.save = function(form) {
    var dfd = $q.defer(),
        data = angular.copy($scope.context);
    
    data.resource_mapping = $scope.mapping;
    var res = $http.post(data.api_url, data);
    res.success(function(data) {
      $scope.context = data;
      dfd.resolve();
    });
    res.error(Validation.handle(form));
    return dfd.promise;
  };

  $scope.toggleActive = function() {
    $scope.context.active = !$scope.context.active;
    $scope.save();
  };

  $scope.isActive = function() {
    return $scope.context.active;
  };

  $scope.import = function(form) {
    if (!$scope.canImport()) {
      return;
    }
    $scope.save(form).then(function() {
      importStarted = true;
      $http.post(upload.api_url).then(function(res) {
        refreshData();
        importStarted = false;
      });
    });
  };

  $scope.uploadFile = function(){
    var d = $modal.open({
      templateUrl: '/static/templates/imports/upload.html',
      controller: 'UploadCtrl',
      resolve: {}
    });
  };

  refreshData();
}]);
