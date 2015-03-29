nomenklatura.directive('nkAuthz', ['$timeout', 'Session', function ($timeout, Session) {
  return {
    restrict: 'AE',
    scope: {
      'operation': '@op',
    },
    link: function (scope, element, attrs, model) {
      element.addClass('hidden');
      Session.get(function(res) {
        if (res.permissions[scope.operation]) {
          element.removeClass('hidden');
        }
      });

    }
  };
}]);


