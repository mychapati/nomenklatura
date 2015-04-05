
nomenklatura.controller('EnrichmentReviewCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$http', 'Flash', 'Meta',
  function ($scope, $routeParams, $location, $timeout, $http, Flash, Meta) {
  var url = '/api/2/enrichment/' + $routeParams.root,
      waitTimeout = null;

  $scope.schema = Meta.schema;
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
    context.enrich_status = status;
    $http.post(url, context).then(function() {
      getNext();
    });
  };

  $scope.getStatements = function() {
    var statements = [];
    angular.forEach($scope.candidate.statements, function(s) {
      s.attr = Meta.schema.qualified[s.attribute];
      if (['label', 'links', 'type'].indexOf(s.attr.name) != -1) {
        return;
      }
      s.subject_entity = $scope.candidate.entities[s.subject];
      s.value_entity = $scope.candidate.entities[s.value];
      statements.push(s);
    });
    statements.sort(function(a, b) {
      if (a.subject == b.subject) {
        if (a.attr.name == 'same_as') return -1;
        if (b.attr.name == 'same_as') return 1;
        if (!a.value_entity && b.value_entity) return 1;
        if (a.value_entity && !b.value_entity) return -1;
        if (!a.value_entity && b.value_entity) return 1;
      } else {
        if (a.value == $scope.candidate.context.enrich_root) return -1;
        if (b.value == $scope.candidate.context.enrich_root) return 1;
        return a.subject.localeCompare(b.subject);
      }
      return 0;
    });
    return statements;
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
