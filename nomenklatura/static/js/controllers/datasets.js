
var loadDataset = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
  Session.get(function(s) {
    var params = {params: {_uid: s.cbq}};
    $http.get('/api/2/datasets/' + $route.current.params.dataset, params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


var loadDatasetEntities = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer();
      
  Session.get(function(s) {
    var url = '/api/2/datasets/' + $route.current.params.dataset + '/entities';
    var params = {params: {_uid: s.cbq}};
    $http.get(url, params).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


var loadRoleUsers = ['$route', '$http', '$q', 'Session', function($route, $http, $q, Session) {
  var dfd = $q.defer(),
      url = '/api/2/datasets/' + $route.current.params.dataset + '/roles';

  Session.get(function(s) {
    var params = {params: {_uid: s.cbq}};
    $q.all([
      $http.get('/api/2/users', params),
      $http.get(url, params)
    ]).then(function(res) {
      var users = res[0].data;

      angular.forEach(users.results, function(u) {
        u.role = 'none';
      });

      angular.forEach(res[1].data.results, function(r) {
        angular.forEach(users.results, function(u) {
          if (r.user_id == u.id) {
            u.role = r.role;
          }
        });
      });

      dfd.resolve(users);
    });
  });

  return dfd.promise;

}];


nomenklatura.controller('DatasetsViewCtrl', ['$scope', '$routeParams', '$location', '$http', '$modal',
                                             '$timeout', 'Validation', 'dataset', 'schema', 'entities',
    function ($scope, $routeParams, $location, $http, $modal, $timeout, Validation, dataset, schema, entities) {

    $scope.dataset = dataset;
    $scope.schema = schema;
    $scope.entities = entities;
    $scope.new_entity = {};
    $scope.query = '';

    $scope.loadEntities = function(url, params) {
        $http.get(url, {params: params}).then(function(res) {
            $scope.entities = res.data;
        });
    };

    var filterTimeout = null;

    $scope.updateFilter = function() {
        if (filterTimeout) { $timeout.cancel(filterTimeout); }

        filterTimeout = $timeout(function() {
            var fparams = {prefix: $scope.query},
                url = '/api/2/datasets/' + dataset.slug + '/entities';
            $scope.loadEntities(url, fparams);
        }, 500);
    };

    $scope.uploadFile = function(){
        var d = $modal.open({
            templateUrl: '/static/templates/imports/upload.html',
            controller: 'UploadCtrl',
            resolve: {
                dataset: function () { return $scope.dataset; }
            }
        });
    };

    $scope.createEntity = function(form) {
        var res = $http.post('/api/2/datasets/' + dataset.slug + '/entities', $scope.new_entity);
        res.success(function(data) {
            $location.path('/datasets/' + dataset.slug + '/entities/' + data.id);
        });
        res.error(Validation.handle(form));
    };
}]);


nomenklatura.controller('DatasetsNewCtrl', ['$scope', '$routeParams', '$modalInstance', '$location', '$http', 'Validation',
  function ($scope, $routeParams, $modalInstance, $location, $http, Validation) {
  $scope.dataset = {};

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.create = function(form) {
    var res = $http.post('/api/2/datasets', $scope.dataset);
    res.success(function(data) {
      $location.path('/datasets/' + data.slug);
      $modalInstance.dismiss('ok');
    });
    res.error(Validation.handle(form));
  };
}]);


nomenklatura.controller('DatasetsSettingsCtrl', ['$scope', '$route', '$routeParams', '$location', '$http', 'Validation', 'dataset', 'users',
  function ($scope, $route, $routeParams, $location, $http, Validation, dataset, users) {
  $scope.dataset = dataset;
  $scope.users = users;

  $scope.roleChange = function(user) {
    var data = {'user': user.id, 'role': user.role};
    $http.post(dataset.api_url + '/roles', data);
  };

  $scope.readonlyRole = function(user) {
    return user.id == $scope.session.user.id;
  };

  $scope.update = function(form) {
    var res = $http.post('/api/2/datasets/' + $scope.dataset.slug, $scope.dataset);
    res.success(function(data) {
      $location.path('/datasets/' + $scope.dataset.slug);
    });
    res.error(Validation.handle(form));
  };
}]);
