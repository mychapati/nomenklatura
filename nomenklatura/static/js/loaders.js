
var loadEntity = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/2/entities/' + $route.current.params.id;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadEntities = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
      
  Session.get(function(s) {
    if (!s.permissions['read']) {
      return dfd.resolve({});
    }
    var params = {params: {_uid: s.cbq}};
    $http.get('/api/2/entities', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


var loadUsers = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();

  Session.get(function(s) {
    var params = {params: {_uid: s.cbq}};
    $http.get('/api/2/users', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });

  return dfd.promise;
}];


var loadImports = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
      
  Session.get(function(s) {
    var params = {params: {_uid: s.cbq, imports: true}};
    $http.get('/api/2/contexts', params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];

