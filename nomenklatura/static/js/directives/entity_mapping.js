
nomenklatura.directive('entityMapping', ['RecursionHelper', function (RecursionHelper) {
    return {
        restrict: 'E',
        scope: {
          'schema': '=',
          'mapping': '=',
          'fields': '='
        },
        templateUrl: '/static/templates/imports/entity.html',
        compile: function(element) {
          return RecursionHelper.compile(element, function(scope, iElement, iAttrs, controller, transcludeFn){
            scope.getTypes = function() {
              var types = [];
              angular.forEach(scope.schema.types, function(t) {
                if (!t.abstract) {
                  types.push(t);  
                }
              });
              return types;
            };

            scope.getAttributes = function() {
              if (!scope.mapping.type) {
                return [];
              }
              var type = scope.schema.types[scope.mapping.type],
                  attributes = [];
              angular.forEach(type.attributes, function(a) {
                if (!angular.isDefined(scope.mapping[a.name])) {
                  attributes.push(a);
                }
              });
              return attributes;
            };

            scope.getFields = function() {
              var fields = []
              angular.forEach(scope.fields, function(f) {
                fields.push(f);
              });
              return fields;
            };

            scope.getSamples = function(field) {
              var totalLen = 0, samples = [];
              angular.forEach(field.samples, function(s) {
                s = s + '';
                if (totalLen <= 100) {
                  samples.push(s);
                  totalLen += s.length;
                }
              });
              return samples;
            };

            scope.getMapped = function() {
              var mapped = {};
              angular.forEach(scope.mapping, function(spec, attr) {
                if (attr != 'type' && scope.schema.attributes[attr]) {
                  mapped[attr] = spec;
                }
              });
              return mapped;
            };

            scope.mapAttribute = function(attribute) {
              scope.mapping[attribute] = {
                  'field': scope.getFields()[0].name,
                  'key': attribute == 'label'
              };
              if (scope.getAttributes().length) {
                scope.newAttribute = scope.getAttributes()[0].name;
              }
            };

            scope.unmapAttribute = function(attribute) {
              delete scope.mapping[attribute];
            };

            scope.mapping = scope.mapping || {};
            scope.mapping.type = scope.mapping.type || scope.getTypes()[0].name;
            scope.newAttribute = scope.getAttributes()[0].name;
          });
        },
    };
}]);
