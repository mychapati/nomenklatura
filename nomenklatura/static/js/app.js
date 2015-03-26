var nomenklatura = angular.module('nomenklatura', ['ngRoute', 'RecursionHelper', 'ngUpload', 'angular-loading-bar', 'ui.bootstrap']);

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

  $routeProvider.when('/login', {
    templateUrl: '/static/templates/users/login.html',
    controller: 'UsersLoginCtrl'
  });

  $routeProvider.when('/datasets/:dataset', {
    templateUrl: '/static/templates/datasets/view.html',
    controller: 'DatasetsViewCtrl',
    resolve: {
      'dataset': loadDataset,
      'entities': loadDatasetEntities,
      'schema': loadSchema
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

  $routeProvider.when('/datasets/:dataset/imports/:context', {
    templateUrl: '/static/templates/imports/mapping.html',
    controller: 'ImportsMappingCtrl',
    resolve: {
      'dataset': loadDataset,
      'upload': loadUpload,
      'schema': loadSchema
    }
  });

  $routeProvider.when('/datasets/:dataset/imports/:context/status', {
    templateUrl: '/static/templates/imports/status.html',
    controller: 'ImportsStatusCtrl',
    resolve: {
      'dataset': loadDataset,
      'upload': loadUpload
    }
  });

  $routeProvider.when('/datasets/:dataset/review/:what', {
    templateUrl: '/static/templates/review.html',
    controller: 'ReviewCtrl',
    resolve: {
      'dataset': loadDataset,
      'schema': loadSchema
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
