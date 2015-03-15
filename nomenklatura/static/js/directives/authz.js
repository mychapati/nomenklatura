nomenklatura.directive('nkAuthz', ['$timeout', 'session', function ($timeout, session) {
    return {
        restrict: 'AE',
        scope: {
            'dataset': '=',
            'operation': '@op',
        },
        link: function (scope, element, attrs, model) {
            element.addClass('hidden');
            scope.$watch('dataset', function(n, o, dataset) {
                if (scope.dataset && scope.dataset.name) {
                    session.get(function(res) {
                        if (res.permissions[scope.operation].indexOf(scope.dataset.name) != -1) {
                            element.removeClass('hidden');
                        }
                    });
                }
            });
        }
    };
}]);
