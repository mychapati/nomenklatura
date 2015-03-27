nomenklatura.directive('nkAttribute', ['$timeout', function ($timeout) {
    return {
        restrict: 'AE',
        scope: {
            'attribute': '=',
            'value': '='
        },
        templateUrl: '/static/templates/attribute.html',
        link: function (scope, element, attrs, model) {
            scope.isEntity = function() {
                return scope.attribute.data_type === 'entity';
            };

            scope.uiUrl = function() {
                if (scope.value.api_url) {
                    return scope.value.api_url.split('/api/2')[1];    
                }
            };
        }
    };
}]);
