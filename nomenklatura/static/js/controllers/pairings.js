
nomenklatura.directive('nkPairingItem', ['$timeout', function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            'entity': '=',
            'schema': '='
        },
        templateUrl: '/static/templates/review_item.html',
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


nomenklatura.controller('PairingsReviewCtrl', ['$scope', '$routeParams', '$location', '$document', '$timeout', '$http', 'schema',
  function ($scope, $routeParams, $location, $document, $timeout, $http, schema) {
  var pairingUrl = '/api/2/pairings',
      nextPairing = null,
      seen = [];

  $scope.schema = schema;
  $scope.pairing = {};


  var loadNext = function(exclude) {
    var params = {params: {exclude: seen}, ignoreLoadingBar: true};
    nextPairing = $http.get(pairingUrl, params);
  };

  var getNext = function() {
    nextPairing.then(function(res) {
      nextPairing = null;
      $scope.pairing = res.data;
      seen.push(res.data.pairing.id);
      seen = seen.splice(seen.length - 6);
      loadNext();
    })
  };

  $scope.hasPairing = function() {
    return $scope.pairing.pairing && $scope.pairing.pairing.id;
  };

  $scope.decide = function(decision) {
    var pairing = angular.copy($scope.pairing.pairing);
    $scope.pairing = {};
    pairing.decision = decision;
    pairing.decided = true;
    $http.post(pairingUrl, pairing);
    getNext();
  };
  
  loadNext();
  getNext();

  $document.bind("keypress", function (event) {
    //console.log(event.keyCode, event.which);
    //if(event.which === 105) { // i
    //  $scope.decide(null)
    //}
    if(event.which === 120) { // x
      $scope.decide(true)
    }
    if(event.which === 121) { // x
      $scope.decide(true)
    }
    if(event.which === 110) { // n
      $scope.decide(false)
    }
  });

}]);
