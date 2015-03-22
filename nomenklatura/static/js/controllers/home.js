var loadDatasets = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
  Session.get(function(s) {
    var params = {params: {_uid: s.cbq, limit: 10}};
    $http.get('/api/2/datasets', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


nomenklatura.controller('HomeCtrl', ['$scope', '$location', '$http', '$modal', 'datasets',
  function ($scope, $location, $http, $modal, datasets) {
  $scope.datasets = datasets;

  $scope.loadDatasets = function(url) {
    $http.get(url).then(function(data) {
      $scope.datasets = data.data;
    });
  };
  
  $scope.newDataset = function(){
    var d = $modal.open({
      templateUrl: '/static/templates/datasets/new.html',
      controller: 'DatasetsNewCtrl'
    });
  };
}]);
