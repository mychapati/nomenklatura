
nomenklatura.controller('EnrichmentReviewCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$http', 'Flash', 'schema',
  function ($scope, $routeParams, $location, $timeout, $http, Flash, schema) {
  var url = '/api/2/enrichment/' + $routeParams.root,
      waitTimeout = null;

  $scope.schema = schema;
  $scope.candidate = {};

  var loadContext = function() {
    if(angular.isDefined($routeParams.id)) {
      $http.get(url + '/' + $routeParams.id).then(function(res) {
        $scope.candidate = res.data;
      });
    } else {
      getNext();
    }
  };

  var getNext = function() {
    var params = {params: {exclude: $routeParams.id}, ignoreLoadingBar: true};
    $http.get(url + '/next', params).then(function(res) {
      if (res.data.status == 'next') {
        $location.path('/manage/enrichment/' + $routeParams.root + '/' + res.data.next);
      }
      if (res.data.status == 'done') {
        Flash.message('All done!', 'success');
        $location.path('/manage');
      }
      if (res.data.status == 'wait') {
        waitTimeout = $timeout(getNext, 1000);
      }
    })
  };

  $scope.hasContext = function() {
    return $scope.candidate.context && $scope.candidate.context.id;
  };

  $scope.decide = function(status) {
    var context = angular.copy($scope.candidate.context);
    $scope.candidate = {};
    pairing.enrich_status = status;
    $http.post(url, pairing).then(function() {
      getNext();
    });
  };
  
  loadContext();

  $scope.$on("$destroy", function() {
    $timeout.cancel(waitTimeout);
  });

  $scope.$on("keypress", function (event, which) {
    if(which === 120) { // x
      $scope.decide('accepted')
    }
    if(which === 121) { // x
      $scope.decide('accepted')
    }
    if(which === 110) { // n
      $scope.decide('rejected')
    }
  });

}]);
