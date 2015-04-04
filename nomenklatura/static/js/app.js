
angular.module('nk.config', [])
    .constant('config', STATIC_CONFIG);

var nomenklatura = angular.module('nomenklatura', ['nk.config', 'ngRoute', 'angularMoment', 'RecursionHelper', 'ngUpload', 'angular-loading-bar', 'ui.bootstrap']);

nomenklatura.config(['$routeProvider', '$locationProvider', '$sceProvider', 'cfpLoadingBarProvider',
    function($routeProvider, $locationProvider, $sceProvider, cfpLoadingBarProvider) {

  cfpLoadingBarProvider.includeSpinner = false;

  $routeProvider.when('/', {
    templateUrl: '/static/templates/index.html',
    controller: 'IndexCtrl',
    resolve: {
      'entities': loadEntities,
      'schema': loadSchema
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

  $routeProvider.when('/settings', {
    templateUrl: '/static/templates/settings.html',
    controller: 'SettingsCtrl',
    resolve: {
      'users': loadRoleUsers
    }
  });

  $routeProvider.when('/imports', {
    templateUrl: '/static/templates/imports/index.html',
    controller: 'ImportsIndexCtrl',
    resolve: {
      'imports': loadImports,
      'schema': loadSchema
    }
  });

  $routeProvider.when('/imports/:context', {
    templateUrl: '/static/templates/imports/mapping.html',
    controller: 'ImportsMappingCtrl',
    resolve: {
      'upload': loadUpload,
      'schema': loadSchema
    }
  });

  $routeProvider.when('/imports/:context/status', {
    templateUrl: '/static/templates/imports/status.html',
    controller: 'ImportsStatusCtrl',
    resolve: {
      'upload': loadUpload
    }
  });

  $routeProvider.when('/manage/dedupe', {
    templateUrl: '/static/templates/tools/dedupe.html',
    controller: 'DedupeReviewCtrl',
    resolve: {'schema': loadSchema}
  });

  $routeProvider.when('/manage/dedupe/:id', {
    templateUrl: '/static/templates/tools/dedupe.html',
    controller: 'DedupeReviewCtrl',
    resolve: {'schema': loadSchema}
  });

  $routeProvider.when('/manage/enrichment/:root', {
    templateUrl: '/static/templates/tools/enrich.html',
    controller: 'EnrichmentReviewCtrl',
    resolve: {'schema': loadSchema}
  });

  $routeProvider.when('/manage/enrichment/:root/:id', {
    templateUrl: '/static/templates/tools/enrich.html',
    controller: 'EnrichmentReviewCtrl',
    resolve: {'schema': loadSchema}
  });

  $routeProvider.when('/entities/:id', {
    templateUrl: '/static/templates/entities/view.html',
    controller: 'EntitiesViewCtrl',
    resolve: {
      'entity': loadEntity,
      'schema': loadSchema
    }
  });

  $routeProvider.otherwise({
    redirectTo: '/'
  });

  $locationProvider.html5Mode(true);
}]);
