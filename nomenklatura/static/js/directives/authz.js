nomenklatura.directive('nkAuthz', ['$timeout', 'Session', function ($timeout, Session) {
    return {
        restrict: 'AE',
        scope: {
            'dataset': '=',
            'operation': '@op',
        },
        link: function (scope, element, attrs, model) {
            element.addClass('hidden');
            scope.$watch('dataset', function(n, o, dataset) {
                if (scope.dataset && scope.dataset.slug) {
                    Session.get(function(res) {
                        if (res.permissions[scope.operation].indexOf(scope.dataset.slug) != -1) {
                            element.removeClass('hidden');
                        }
                    });
                }
            });
        }
    };
}]);


