import os
from fabric.api import cd, env, task, require, sudo, prefix, shell_env, run
from fabric.contrib.files import exists, upload_template


REPO_URL = 'https://github.com/pudo/nomenklatura.git'
PACKAGES = (
    'git-core',
    'nginx',
    # 'npm',
    'python-dev',
    'python-virtualenv',
    'supervisor',
)


@task
def mozambique():
    env.user = 'mozambique'
    env.hosts = ['ec2-54-76-245-198.eu-west-1.compute.amazonaws.com']
    env.server_name = 'mozambique.connectedafrica.org'
    env.deploy_dir = '/home/mozambique/deploy'
    env.config_file = '/home/mozambique/settings.py'
    env.branch = 'master'
    env.nginx_bind = '127.0.0.1:80'
    env.proxy_port = 5050
    env.proxy_host = '127.0.0.1'


@task
def ttip():
    # TODO
    pass


@task
def provision():
    require('user', 'deploy_dir')

    sudo('apt-get install %s --no-upgrade' % ' '.join(PACKAGES))
    sudo('apt-get build-dep lxml --no-upgrade')
    sudo('mkdir -p %s' % env.deploy_dir)
    sudo('chown -R %s:%s %s' % (env.user, env.user, env.deploy_dir))


@task
def deploy():
    require('user', 'deploy_dir', 'branch')

    repo_dir = os.path.join(env.deploy_dir, 'nomenklatura')
    ve_dir = os.path.join(env.deploy_dir, 'env')
    log_dir = os.path.join(env.deploy_dir, 'logs')

    if not exists(ve_dir):
        run('virtualenv -p python2.7 %s' % ve_dir)

    with cd(env.deploy_dir):
        run('rm -rf %s' % repo_dir)
        run('git clone -b %s %s %s' % (env.branch, REPO_URL, repo_dir))

    kw = {'NOMENKLATURA_SETTINGS': env.config_file}
    with cd(repo_dir), prefix('. %s/bin/activate' % ve_dir), shell_env(**kw):
        run('pip install "numpy>=1.9"')
        run('pip install -r requirements.txt')
        run('pip install gunicorn')
        run('pip install -e ./')
        run('bower install')
        run('python nomenklatura/manage.py sync')
        run('python nomenklatura/manage.py assets --parse-templates build')

    # render and upload templates
    deploy_dir = os.path.join(os.path.dirname(__file__), 'deploy')
    upload_template(os.path.join(deploy_dir, 'nginx.template'),
                    '/etc/nginx/sites-enabled/%s' % env.server_name,
                    get_nginx_template_context(repo_dir, ve_dir, log_dir),
                    use_sudo=True, backup=False)
    upload_template(os.path.join(deploy_dir, 'supervisor.template'),
                    '/etc/supervisor/conf.d/%s.conf' % env.server_name,
                    get_supervisor_template_context(repo_dir, ve_dir, log_dir),
                    use_sudo=True, backup=False)
    # make sure logging dir exists and update processes
    run('mkdir -p %s' % log_dir)
    sudo('supervisorctl reload')
    sudo('/etc/init.d/nginx reload')
    sudo('/etc/init.d/varnish restart')


def get_nginx_template_context(repo_dir, ve_dir, log_dir):
    return {
        'server-name': env.server_name,
        'server-port': env.nginx_bind,
        'static-path': os.path.join(repo_dir, 'nomenklatura/static/'),
        'proxy-host': env.proxy_host,
        'proxy-port': env.proxy_port,
    }


def get_supervisor_template_context(repo_dir, ve_dir, log_dir):
    return {
        'user': env.user,
        'server-name': env.server_name,
        'project-dir': repo_dir,
        've-dir': ve_dir,
        'log-dir': log_dir,
        'host': env.proxy_host,
        'port': env.proxy_port,
        'config-file': env.config_file,
        'process-name': '%(program_name)s_%(process_num)s'
    }
