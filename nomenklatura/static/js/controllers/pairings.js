
nomenklatura.directive('nkPairingItem', ['$timeout', function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            'entity': '=',
            'schema': '='
        },
        templateUrl: '/static/templates/review_item.html',
        link: function (scope, element, attrs, model) {
          //
        }
    };
}]);


nomenklatura.controller('PairingsReviewCtrl', ['$scope', '$routeParams', '$location', '$timeout', '$http', 'dataset',
  function ($scope, $routeParams, $location, $timeout, $http, dataset) {
  $scope.dataset = dataset;
  

}]);
