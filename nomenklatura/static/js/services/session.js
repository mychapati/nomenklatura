nomenklatura.factory('session', ['$http', function($http) {
    var dfd = null;

    var get = function(cb) {
        if (dfd === null) {
            var dt = new Date();
            var config = {cache: false, params: {'_': dt.getTime()}};
            dfd = $http.get('/api/2/sessions', config);
        }
        dfd.success(function(data) {
          data.cbq = data.logged_in ? data.user.id : 'anon';
          cb(data);
        });
    };

    var reset = function() {
        dfd = null;
    };

    return {
        get: get,
        reset: reset
    };
}]);
