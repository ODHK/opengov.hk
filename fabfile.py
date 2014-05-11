#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, posixpath
from time import time
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists, append

## GLOBALS

env.project_name = 'opengov'          # e.g. 'opengov'
env.project_url = 'opengov.hk'        # e.g. 'opengov.hk'
env.hosts = ['128.199.212.155']       # default to open platform
env.path = '/var/www/%(project_url)s' % env
env.user = 'su_opengov'

env.github_account = 'ODHK'               # e.g. 'ODHK'
env.github_repo = 'opengov.hk'                  # e.g. 'opengov.hk'
env.setup_github = True

env.key_filename = "~/.ssh/id_rsa"
env.colorize_errors = True
env.env_file = "requirements.txt"

## ENVIRONMENTS

def localhost():
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = 'io'
    env.path = '/srv/www/%(project_url)s' % env
    env.env_file = "requirements.txt"
    env.setup_github = False
    paths()

def platform():
    "Use the open platform"
    env.hosts = ['opengov.hk']
    env.user = 'su_opengov'
    env.path = '/var/www/%(project_url)s' % env
    env.env_file = "requirements.txt"
    env.github_email = 'info@opengov.hk'
    env.github_name = 'OpenGov.HK Admin'
    env.setup_github = True
    paths()

def ds1(student):
    "DS1 Playground"
    env.hosts = ['opengov.hk']
    env.user = "ds1-%s" % student
    env.path = '/var/www/%(project_url)s' % env
    env.env_file = "requirements.txt"
    env.github_email = 'info@opengov.hk'
    env.github_name = 'OpenGov.HK Admin'
    env.setup_github = True
    paths()


def paths():
    env.domain_path = env.path
    env.current_path = "%(domain_path)s/current" % env
    env.releases_path = "%(domain_path)s/releases" % env
    env.shared_path = "%(domain_path)s/shared" % env

## TASKS

# Setup

def setup(update=False,shell=False):
    """
    Update the installed packages and decide how to setup the system depending on the OS
    """
    require('hosts', provided_by=[localhost,platform])

    env.os = osname()

    if update:
        update_system()

    if shell:
        setup_shell()

    if env.os == 'Ubuntu':
        setup_ubuntu()
    elif env.os == 'Fedora':
        setup_fedora()
    elif env.os == 'OSX':
        setup_osx()

# Deployment

def prepare_deploy():
    test()
    commit()
    push()

def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and
    then restart the platform
    """
    require('hosts', provided_by=[localhost,platform])

    releases()
    checkout()
    update_env()
    install_site()
    symlink()
    migrate()
    cleanup()
    restart()

def hotfix():
    """
    Deploy a hotfix to to server. Does not create a new release directory, does
    not install any dependencies, also does not restart the server.
    """
    releases()
    with cd(env.current_path):
        pull()

def rollback():
    """Rolls back to a previous version and restarts"""
    releases()
    rollback_code()
    restart()

# Test

def test():
    with settings(warn_only=True):
        result = local('./manage.py test $(project_name)', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

# User Management

def create_user(username, password, admin='no'):
    "Create unix user, supply admin=yes for sudo enabled accounts"
    with settings(user='root'):

        if admin == 'yes':
        # Create the admin group and add it to the sudoers file
            admin_group = 'admin'
            run('addgroup {group}'.format(group=admin_group))
            run('echo "%{group} ALL=(ALL) ALL" >> /etc/sudoers'.format(
                group=admin_group))

        # Create the new user (default group=username);
        run('adduser {username} --disabled-password --gecos ""'.format(
            username=username))

        # add to admin group
        if admin == 'yes':
            run('adduser {username} {group}'.format(
                username=username,
                group=admin_group))

        # Set the password for the new admin user
        run('echo "{username}:{password}" | chpasswd'.format(
            username=username,
            password=password))

def promote_to_admin(username):
    with settings(user='root'):
        run('adduser {username} {group}'.format(
            username=username,
            group='admin'))

def create_django_admin():
    with cd(env.current_release):
        run('python manage.py createsuperuser')

# SSH Key Management

def generate_deploy_key():
    run('ssh-keygen -t rsa -C "%(github_email)s"' % env)
    run('cat ~/.ssh/id_rsa.pub')

def push_key(key_file='~/.ssh/id_rsa.pub'):
    key_text = read_key_file(key_file)
    append('~/.ssh/authorized_keys', key_text)

# Maintenance Mode

def enable():
    """Makes the application web-accessible again"""
    run("rm %(shared_path)s/system/maintenance.html" % env )

def disable(**kwargs):
    """Present a maintenance page to visitors"""
    import os, datetime
    from django.conf import settings
    try:
        settings.configure(
            DEBUG=False, TEMPLATE_DEBUG=False,
            TEMPLATE_DIRS=(os.path.join(os.getcwd(), 'templates/'),)
        )
    except EnvironmentError:
        pass
    from django.template.loader import render_to_string
    env.deadline = kwargs.get('deadline', None)
    env.reason = kwargs.get('reason', None)
    open("maintenance.html", "w").write(
        render_to_string("maintenance.html", { 'now':datetime.datetime.now(), 'deadline':env.deadline, 'reason':env.reason }).encode('utf-8')
    )
    put('maintenance.html', '%(shared_path)s/system/maintenance.html' % { 'shared_path':env.shared_path })
    local("rm maintenance.html")

## HELPER METHODS

# Setup

def update_system():
    """
    Update and Upgrade system packages
    """
    require('hosts', provided_by=[localhost,platform])
    require('os', provided_by=[localhost,platform])
    require('path')

    if env.os == 'Ubuntu':
        sudo('apt-get update')
        sudo('apt-get -y upgrade')
    elif env.os == 'Fedora':
        sudo('yum update -y')

def setup_shell():
    with cd('$HOME'):
        run('curl -L http://install.ohmyz.sh | sh')
        sudo('chsh $USER -s $(which zsh);')
        run('usermod -s $(which zsh);')
        run('curl https://gist.githubusercontent.com/tijptjik/97e1e0380a21249b49d9/raw/9071ee07f29cad69cad70d82d3f1f55033080561/prose.zsh-theme >> .oh-my-zsh/themes/prose.zsh-theme')
        run('mkdir -p $HOME/.tools')
        with settings(warn_only=True):
            run('git clone https://github.com/rupa/z.git $HOME/.tools/z')
        run('curl https://gist.githubusercontent.com/tijptjik/ac9555e37364287aac37/raw/ecd9fec1fb1e5e4de1181e31e852ddb7205c640b/.zshrc > .zshrc'    )
        run('source $HOME/.zshrc')

def setup_ubuntu():
    """
    Update the Ubuntu host and install the necessary third party software, then
    follow the setup steps all OSes have in common
    """
    sudo('apt-get install -y python-setuptools python-dev')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('apt-get install -y git zsh htop links')
    sudo('apt-get install -y nginx')
    sudo('apt-get install -y postgresql postgresql-contrib python-psycopg2 libpq-dev')
    sudo('apt-get install -y libxml2 libxslt1.1 libxslt1-dev')
    setup_common()

def setup_fedora():
    """
    Update the Fedora host and install the necessary third party software, then
    follow the setup steps all OSes have in common
    """
    sudo('yum install -y python-devel python-pip')
    sudo('pip install virtualenv')
    sudo('yum install -y nginx git postgresql postgresql-devel postgresql-server libxml2 libxml2-python')
    setup_common()

def setup_osx():
    """
    Requires brew. Update the OSX host and install the necessary third party software, then
    follow the setup steps all OSes have in common.
    """
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('brew install nginx')
    setup_common()

def setup_common():
    setup_user_dir()
    setup_github()
    prepare_nginx()
    setup_release_dirs()
    deploy()

# Package Setup

def install_site():
    "Add the virtualhost file to nginx"
    with settings(warn_only=True):
        sudo('cp %(current_release)s/conf/%(project_url)s /etc/nginx/sites-available' % env)
        sudo('ln -s /etc/nginx/sites-available/%(project_url)s /etc/nginx/sites-enabled/%(project_url)s' % env)

def update_env():
    "Install the required packages from the requirements file using pip"
    run("cd %(current_release)s; virtualenv --no-site-packages --unzip-setuptools env" % env )
    with prefix(". %(current_release)s/env/bin/activate" % env):
        sudo("pip install -r %(current_release)s/%(env_file)s" % env )

    # sudo("pip install -r %(current_release)s/%(env_file)s -e %(current_release)s" % env )
    permissions()

# Release Management

def releases():
    """List a releases made"""
    env.releases = sorted(run('ls -x %(releases_path)s' % env).split())
    if len(env.releases) >= 1:
        env.current_revision = env.releases[-1]
        env.current_release = "%(releases_path)s/%(current_revision)s" % env
    if len(env.releases) > 1:
        env.previous_revision = env.releases[-2]
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % env

def symlink():
    """Updates the symlink to the most recently deployed version"""
    run("ln -nfs %(current_release)s %(current_path)s" % env)
    run("ln -nfs %(shared_path)s/log %(current_release)s/log" % env)
    run("ln -nfs %(shared_path)s/index %(current_release)s/index" % env)
    run("ln -nfs %(shared_path)s/cdlm.db %(current_release)s/cdlm.db" % env)
    # run("ln -nfs %(shared_path)s/system/local.py %(current_release)s/%(project_name)s/local.py" % env)
    # run("ln -nfs %(current_release)s/env/src/django/django/contrib/admin/media %(current_release)s/%(project_name)s/media/admin" % env)

def rollback_code():
    """Rolls back to the previously deployed version"""
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % env
        env.previous_release = "%(releases_path)s/%(previous_revision)s" %  env
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % env)

def cleanup():
    """Clean up old releases"""
    if len(env.releases) > 3:
        directories = env.releases
        directories.reverse()
        del directories[:3]
        env.directories = ' '.join([ "%(releases_path)s/%(release)s" % { 'releases_path':env.releases_path, 'release':release } for release in directories ])
        run("rm -rf %(directories)s" % env)

# Database

def migrate():
    """Run the migrate task"""
    if not env.has_key('current_release'):
        releases()
    # run("%(current_path)s/env/bin/python manage.py syncdb --migrate" % env)
    with prefix(". %(current_release)s/env/bin/activate" % env):
        with cd(env.current_release):
            run("python manage.py syncdb --migrate" % env)

# Housekeeping

def setup_user_dir():
    sudo('mkdir -p %(path)s; chown %(user)s:%(user)s %(path)s;' % env, pty=True)

def setup_github():
    if (env.setup_github):
        run('git config --global user.email %(github_email)s' % env)
        run('git config --global user.name %(github_name)s' % env)

def prepare_nginx():
    with settings(warn_only=True):
        sudo('mkdir -p /etc/nginx/{sites-available,sites-enabled}')
        with cd('/etc/nginx/sites-available'):
            sudo('rm default;')

def setup_release_dirs():
    """Prepares one or more servers for deployment"""
    with cd(env.path) and settings(warn_only=True):
        sudo('virtualenv .;' % env)
        sudo("mkdir -p %(domain_path)s/{releases,shared,packages}" % env)
        sudo("mkdir -p %(shared_path)s/{system,logs,index}" % env)
        permissions()

def permissions():
    """Make the release group-writable"""
    sudo("chmod -R g+w %(domain_path)s" % env)
    sudo("chown -R %(user)s:%(user)s %(domain_path)s" % env)
    run("chmod a+w %(shared_path)s/logs" % env)

# OS

def osname():
    script_file = open('scripts/osdetection.sh')
    os = run(script_file.read())
    script_file.close()
    return os

# Security

def read_key_file(key_file):
    key_file = os.path.expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()

# Nginx

def start():
    "Restart the web server"
    sudo('service nginx restart')

def restart():
    "Restart the web server"
    sudo('service nginx restart')

def stop():
    "Stop the web server"
    sudo('service nginx stop')

# Git Commands

def init():
    run("git init")
    run("git remote add origin git@github.com:%(github_account)s/%(github_repo)s.git" % env)
    run("git fetch origin")
    run("git checkout -b master --track origin/master")

def clone():
    run("git clone -q -o origin --depth 1 git@github.com:%(github_account)s/%(github_repo)s.git %(current_release)s" % env)

def fetch():
    run("git fetch origin")

def pull():
    run("git pull origin master")

def commit():
    local("git add -p && git commit")

def push():
    local("git push")

def checkout():
    """Checkout code to the remote servers"""
    env.time = time()
    env.current_release = "%(releases_path)s/%(time).0f" % env
    with cd(env.releases_path):
        clone()
