from fabric.api import (local,    # for local command
                        run,      # for remote command
                        env,
                        task,
                        roles,
                        execute,
                        runs_once,
                        put)

from fabric.context_managers import (cd,
                                     lcd)


PROJECT_NAME = 'webapp-template'


'''
 this script is to deploy {PROJECT_NAME} automatically

 before starting, you should checkout the latest version
 of pn in seperate place just for deploy.

 steps as following:

 - configure the logger level greater than 'info'
 - be sure at the root of project, and exec: 'fab deploy'

 : target dir tree:
    /opt/www/python27    - the project's python
    /opt/www/pn     - the main project
    /opt/www/supervisor_rt
                        + /logs
                        + /supervisord.conf
                        + /supervisord.pid
'''

env.roledefs = {
    'online': [
        'root@*.*.*.*',
        'root@*.*.*.*',
    ],
    'test': ['root@10.10.68.117']}


@task
@runs_once
def prepare():
    with lcd('..'):
        local('ls')
        local('if [ -e {pn}/deploy/config.py ]; then '
              'cp {pn}/deploy/config.py {pn}/webapp/conf/;'
              'fi'
              .format(pn=PROJECT_NAME))
        local('if [ -f {pn}.tgz ]; then '
              'mv {pn}.tgz {pn}.tgz.$(date +%Y%m%d%H%M%S);'
              'fi'
              .format(pn=PROJECT_NAME))
        local('tar -czf {pn}.tgz {pn} '
              '--exclude "{pn}/logs/*" '
              '--exclude "{pn}/ux" '
              '--exclude "{pn}/.*"'
              .format(pn=PROJECT_NAME))


@task
@runs_once
def clear():
    pass


@task
def deploy():
    execute(prepare)
    copy_and_restart('config_online.py')


@task
def deploy_test():
    execute(prepare)
    copy_and_restart('config_test.py')


@task
@roles('online')
def copy_and_restart(conf_file_name):
    with cd('/opt'), lcd('..'):
        run('if [ ! -d tmp ]; then mkdir tmp; fi')
        run('if [ -e tmp/{pn}.tgz ]; then '
            'mv tmp/{pn}.tgz tmp/{pn}.tgz.$(date +%Y%m%d%H%M%S);'
            'fi'
            .format(pn=PROJECT_NAME))
        put('{pn}.tgz'.format(pn=PROJECT_NAME), 'tmp')
        with cd('www'):
            run('if [ -d {pn} ]; then '
                'mv {pn} {pn}_$(date +%Y%m%d%H%M%S);'
                'fi'
                .format(pn=PROJECT_NAME))
            run('tar -xzf /opt/tmp/{pn}.tgz'
                .format(pn=PROJECT_NAME))
            run('if [ -e {pn}/deploy/{cfn} ]; then '
                'cp {pn}/deploy/{cfn} {pn}/src/conf/config.py;'
                'fi'
                .format(pn=PROJECT_NAME, cfn=conf_file_name))
            run('if [ ! -f supervisor_rt/supervisord.pid ]; then '
                'supervisord -c supervisor_rt/supervisord.conf;'
                'else kill -HUP $(cat supervisor_rt/supervisord.pid);'
                'fi')
            run('sleep 2;'
                'ps -ef | grep webapp | grep -v grep')
