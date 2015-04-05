
nomenklatura.factory('Meta', ['config', function(config) {

  // Generate a list of attributes by qualified name.
  qualified = {};
  angular.forEach(config.SCHEMA.types, function(t) {
    angular.forEach(t.attributes, function(a) {
      qualified[a.qname] = a;
    });
  });
  config.SCHEMA.qualified = qualified;

  return {
    'name': config.NAME,
    'title': config.TITLE,
    'schema': config.SCHEMA,
  }
}]);
