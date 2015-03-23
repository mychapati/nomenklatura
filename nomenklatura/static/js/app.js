var nomenklatura = angular.module('nomenklatura', ['ngRoute', 'ngUpload', 'angular-loading-bar', 'ui.bootstrap']);

nomenklatura.config(['$routeProvider', '$locationProvider', '$sceProvider', 'cfpLoadingBarProvider',
    function($routeProvider, $locationProvider, $sceProvider, cfpLoadingBarProvider) {

  cfpLoadingBarProvider.includeSpinner = false;

  $routeProvider.when('/', {
    templateUrl: '/static/templates/home.html',
    controller: 'HomeCtrl',
    resolve: {
      'datasets': loadDatasets
    }
  });

  $routeProvider.when('/docs/:page/:anchor', {
    templateUrl: '/static/templates/pages/template.html',
    controller: 'DocsCtrl'
  });

  $routeProvider.when('/docs/:page', {
    templateUrl: '/static/templates/docs/template.html',
    controller: 'DocsCtrl'
  });

  $routeProvider.when('/datasets/:dataset', {
    templateUrl: '/static/templates/datasets/view.html',
    controller: 'DatasetsViewCtrl',
    resolve: {
      'dataset': loadDataset,
      'entities': loadDatasetEntities
    }
  });

  $routeProvider.when('/datasets/:dataset/settings', {
    templateUrl: '/static/templates/datasets/settings.html',
    controller: 'DatasetsSettingsCtrl',
    resolve: {
      'dataset': loadDataset,
      'users': loadRoleUsers
    }
  });

  $routeProvider.when('/datasets/:dataset/uploads/:upload', {
    templateUrl: '/static/templates/mapping.html',
    controller: 'MappingCtrl',
    resolve: {
      'dataset': loadDataset,
      'upload': loadUpload
    }
  });

  $routeProvider.when('/datasets/:dataset/review/:what', {
    templateUrl: '/static/templates/review.html',
    controller: 'ReviewCtrl',
    resolve: {
      'dataset': loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/entities/:id', {
    templateUrl: '/static/templates/entities/view.html',
    controller: 'EntitiesViewCtrl',
    resolve: {
      'dataset': loadDataset,
      'entity': loadEntity,
      'schema': loadSchema
    }
  });

  $routeProvider.otherwise({
    redirectTo: '/'
  });

  $locationProvider.html5Mode(true);
}]);

nomenklatura.handleFormError = function(form) {
  return function(data, status) {
    if (status == 400) {
        var errors = [];
        for (var field in data.errors) {
            form[field].$setValidity('value', false);
            form[field].$message = data.errors[field];
            errors.push(field);
        }
        if (angular.isDefined(form._errors)) {
            angular.forEach(form._errors, function(field) {
                if (errors.indexOf(field) == -1) {
                    form[field].$setValidity('value', true);
                }
            });
        }
        form._errors = errors;
    } else {
      // TODO: where is your god now?
      if (angular.isObject(data) && data.message) {
        alert(data.message);
      }
      //console.log(status, data);
    }
  };
};
