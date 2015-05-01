
nomenklatura.directive('entityMapping', ['RecursionHelper', 'Meta', function (RecursionHelper, Meta) {
    return {
        restrict: 'E',
        scope: {
          'mapping': '=',
          'fields': '='
        },
        templateUrl: '/static/templates/imports/entity.html',
        compile: function(element) {
          return RecursionHelper.compile(element, function(scope, iElement, iAttrs, controller, transcludeFn){

            scope.getTypes = function() {
              var types = [];
              angular.forEach(Meta.schema.types, function(t) {
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
              var type = Meta.schema.types[scope.mapping.type],
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

            scope.getAttribute = function(attr) {
              var type = Meta.schema.types[scope.mapping.type];
              return type.attributes[attr];
            };

            scope.getMapped = function() {
              var mapped = {};
              var type = Meta.schema.types[scope.mapping.type];
              angular.forEach(scope.mapping, function(spec, attr) {
                if (attr != 'type' && type.attributes[attr]) {
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
