from flask.ext.assets import Bundle

from nomenklatura.core import assets

deps_assets = Bundle(
    'vendor/jquery/dist/jquery.js',
    'vendor/bootstrap/js/collapse.js',
    'vendor/angular/angular.js',
    'vendor/moment/moment.js',
    'vendor/angular-route/angular-route.js',
    'vendor/angular-moment/angular-moment.js',
    'vendor/angular-recursion/angular-recursion.js',
    'vendor/angular-loading-bar/build/loading-bar.js',
    'vendor/angular-bootstrap/ui-bootstrap-tpls.js',
    'vendor/ngUpload/ng-upload.js',
    filters='uglifyjs',
    output='assets/deps.js'
)

app_assets = Bundle(
    'js/app.js',
    'js/loaders.js',
    'js/services/meta.js',
    'js/services/session.js',
    'js/services/validation.js',
    'js/services/flash.js',
    'js/directives/pagination.js',
    'js/directives/attribute.js',
    'js/directives/entity_mapping.js',
    'js/directives/authz.js',
    'js/controllers/app.js',
    'js/controllers/manage.js',
    'js/controllers/imports.js',
    'js/controllers/index.js',
    'js/controllers/docs.js',
    'js/controllers/dedupe.js',
    'js/controllers/enrichment.js',
    'js/controllers/settings.js',
    'js/controllers/entities.js',
    'js/controllers/users.js',
    filters='uglifyjs',
    output='assets/app.js'
)

css_assets = Bundle(
    'vendor/font-awesome/less/font-awesome.less',
    'style/style.less',
    filters='less,cssrewrite,cssmin',
    output='assets/style.css'
)

assets.register('deps', deps_assets)
assets.register('app', app_assets)
assets.register('css', css_assets)
