
nomenklatura.directive('nkDedupeItem', ['$timeout', function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            'entity': '=',
            'schema': '='
        },
        templateUrl: '/static/templates/tools/dedupe_item.html',
        link: function (scope, element, attrs, model) {
          scope.type = {};
          scope.rows = [];

          scope.$watch('entity', function(e) {
            if (!e) return;
            scope.type = scope.schema.types[e.type];
            var rows = [];
            angular.forEach(scope.type.attributes, function(a) {
              //if (a.name == 'type') return;
              var value = scope.entity[a.name];
              if (angular.isDefined(value)) {
                rows.push({
                  'attr': a,
                  'value': value
                });
              }
            });
            scope.rows = rows;
          });

        }
    };
}]);


nomenklatura.controller('DedupeReviewCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$http', 'Flash', 'schema',
  function ($scope, $routeParams, $location, $timeout, $http, Flash, schema) {
  var url = '/api/2/pairings';

  $scope.schema = schema;
  $scope.pairing = {};


  var loadPairing = function() {
    if(angular.isDefined($routeParams.id)) {
      $http.get(url + '/' + $routeParams.id).then(function(res) {
        $scope.pairing = res.data;
      });
    } else {
      getNext();
    }
  };

  var getNext = function() {
    var params = {params: {exclude: $routeParams.id}, ignoreLoadingBar: true};
    $http.get(url + '/next', params).then(function(res) {
      if (res.data.status == 'next') {
        $location.path('/manage/dedupe/' + res.data.next);
      }
      if (res.data.status == 'done') {
        Flash.message('All done!', 'success');
        $location.path('/manage');
      }
    })
  };

  $scope.hasPairing = function() {
    return $scope.pairing.pairing && $scope.pairing.pairing.id;
  };

  $scope.decide = function(decision) {
    var pairing = angular.copy($scope.pairing.pairing);
    pairing.decision = decision;
    pairing.decided = true;
    $http.post(url, pairing).then(function() {
      getNext();
    });
  };
  
  loadPairing();

  $scope.$on("keypress", function (event, which) {
    if(which === 120) { // x
      $scope.decide(true)
    }
    if(which === 121) { // x
      $scope.decide(true)
    }
    if(which === 110) { // n
      $scope.decide(false)
    }
  });

}]);
