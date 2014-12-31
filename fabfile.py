from fabric.api import run
from fabric.api import env
from fabric.api import prompt
from fabric.api import execute
from fabric.api import sudo
from fabric.api import cd
from fabric.api import put
import boto.ec2
import time
import os

env.hosts = ['*', ]
env['region'] = 'us-west-2'
env['user'] = 'ubuntu'

import credentials
credentials.set_credentials()


def _move_sources():
    #Code here to check whether the repo has already been cloned
    sudo("git clone https://github.com/charlieRode/django-imagr.git")
    sudo("ln -s " +
        "/home/ubuntu/django-imagr/nginx.conf " +
        "/etc/nginx/sites-enabled/amazonaws.com")

    with cd("django-imagr"):
        put("imagr_site/imagr_site/credentials.py",
            "/home/ubuntu/django-imagr/imagr_site/imagr_site/credentials.py",
            use_sudo=True)


def move_sources():
    run_command(_move_sources)


def _install_pips():
    with cd("django-imagr"):
        sudo("wget http://raw.github.com/pypa/pip/master/contrib/get-pip.py")
        sudo("python get-pip.py")
        sudo("pip install -r requirements.txt")


def install_pips():
    run_command(_install_pips)


def _setup_database():
    password = os.environ['DB_PASSWORD']

    sudo('createdb imagr', user='postgres')

    create_user_sql_query = """"
    CREATE USER imagr WITH password '%s';
    GRANT ALL ON DATABASE imagr TO imagr;"
    """ % password

    sudo('psql -U postgres imagr -c %s' % create_user_sql_query,
         user='postgres')


def setup_database():
    run_command(_setup_database)


def _run_server():
    sudo("/etc/init.d/nginx restart")
    with cd("django-imagr/imagr_site"):
        sudo("python manage.py --noinput migrate")
        sudo("python manage.py --noinput collectstatic")
        run('gunicorn -b 127.0.0.1:8888 imagr_site.wsgi:application')


def run_server():
    run_command(_run_server)


def _lsdir():
    with cd("django-imagr"):
        sudo("ls -a")


def lsdir():
    run_command(_lsdir)


def _setup_imagr_environment():
    """installs all prereq packages onto the ubuntu server instance"""
    time.sleep(60) # wait for server to boot
    sudo("apt-get -y update")
    sudo("apt-get -y upgrade")
    sudo("apt-get -y remove python") # remove current version of python
    sudo("apt-get -y install python-dev")
    sudo("apt-get -y install postgresql-9.3")
    sudo("apt-get -y install postgresql-server-dev-9.3")
    sudo("apt-get -y install git")
    sudo("apt-get -y install nginx")
    sudo("apt-get -y install gunicorn")


def setup_imagr_environment():
    run_command(_setup_imagr_environment)


def _reboot_server():
    sudo("shutdown -r now")


def reboot_server():
    run_command(_reboot_server)


def _which_python():
    sudo("readlink -f $(which python) | xargs -I % sh -c 'echo -n \"%: \"; % -V'")


def which_python():
    run_command(_which_python)


def establish_ec2_connection():
    if 'ec2' not in env:
        conn = boto.ec2.connect_to_region(env.region)
        if conn is not None:
            env.ec2 = conn
            print "Connected to EC2 region %s" % env['region']
        else:
            msg = "Unable to connect to EC2 region %s"
            raise IOError(msg % env['region'])
    return env.ec2


def provision_instance(wait_for_running=False, timeout=60, interval=5):
    conn = establish_ec2_connection()
    instance_type = 't1.micro'
    key_name = 'D2014-11-13'
    security_group = 'ssh-access'
    image_id = 'ami-37501207'

    reservations = conn.run_instances(
        image_id,
        key_name=key_name,
        instance_type=instance_type,
        security_groups=[security_group, ])

    new_instances = [i for i in reservations.instances if i.state == u'pending']
    running_instances = []
    if wait_for_running:
        waited = 0
        while (len(new_instances) > 0) and (timeout - waited > 0):
            time.sleep(int(interval))
            waited += int(interval)
            for instance in new_instances:
                print "Instance %s is %s" % (instance.id, instance.state)
                if instance.state == u'running':
                    running_instances.append(instance)
                instance.update()
            new_instances = [i for i in reservations.instances if i not in running_instances]


def list_instances(verbose=False, state='all'):
    conn = establish_ec2_connection()
    reservations = conn.get_all_reservations()
    instances = []

    for r in reservations:
        for i in r.instances:
            if state == 'all' or state == i.state:
                instance = {
                'id': i.id,
                'type': i.instance_type,
                'image': i.image_id,
                'state': i.state,
                'instance': i
                }
                instances.append(instance)
    env.instances = instances
    if verbose:
        import pprint   # "pretty print"
        pprint.pprint(env.instances)


def select_instance(state='running', default_to_first=False):
    # If an active_instance has already been defined in env, exit the function
    if 'active_instance' in env.keys():
        return

    if default_to_first:
        list_instances(state=state)
        choice = 1
    else:

        list_instances(state=state)  # Set the environment variables so that we have     
                                     # access to env.instances
        if len([instance for instance in env.instances if instance['state'] == state]) == 0:
            print "There are no %s instances" % state
            return -1

        prompt_text = "Please select from the following instances:\n"
        instance_template = " %(ct)d: %(state)s instance %(id)s\n"
        for ct, instance in enumerate(env.instances, 1):
            args = {'ct': ct}
            args.update(instance)
            prompt_text += instance_template % args
        prompt_text += "Choose an instance: "

        def validation(input):
            choice = int(input)
            if not choice in range(1, len(env.instances) + 1):
                raise ValueError("%d is not a valid instance" % choice)
            return choice

        choice = prompt(prompt_text, validate=validation)

    env.active_instance = env.instances[choice - 1]['instance']


def run_command(command, default_to_first=False):
    select_instance(default_to_first=default_to_first)
    selected_hosts = ['ubuntu@' + env.active_instance.public_dns_name]
    execute(command, hosts=selected_hosts)


def run_complete_setup():
    provision_instance(wait_for_running=True)
    run_command(_setup_imagr_environment, default_to_first=True)
    time.sleep(60)

    run_command(_move_sources, default_to_first=True)
    run_command(_install_pips, default_to_first=True)
    run_command(_setup_database, default_to_first=True)
    run_command(_run_server, default_to_first=True)


def _create_superuser():
    with cd('django-imagr/imagr_site'):
        sudo('python manage.py --noinput migrate')
        sudo('python manage.py -noinput createsuperuser') #the single-dash is taken from Ben's and Charles' fabfile example


def create_superuser():
    run_command(_create_superuser, default_to_first=True)


def _setup_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')


def setup_nginx():
    run_command(_setup_nginx)


def print_dns():
    select_instance()
    print env.active_instance.public_dns_name


def stop_instance(wait_for_stopped=False, timeout=60, wait=5):
    running_instances = select_instance() # returns -1 if there are no running instances
    if running_instances == -1:
        return
    instance = env.active_instance
    timeout = int(timeout)
    wait = int(wait)
    choice = prompt("Would you like to stop instance %s [y/n]?" % instance.id)
    if choice.lower() != 'y':
        return
    env.ec2.stop_instances(instance_ids=[instance.id])
    if wait_for_stopped:
        waited = 0
        while instance.state != u'stopped' and (timeout - waited > 0):
            time.sleep(wait)
            waited += wait
            instance.update()
            print "Instance %s is %s" % (instance.id, instance.state)


def terminate_instance(wait_for_terminated=False, timeout=60, wait=5):
    stopped_instances = select_instance(state='stopped') # returns -1 if there are no stopped instances
    if stopped_instances == -1:
        return
    instance = env.active_instance
    timeout = int(timeout)
    wait = int(wait)
    choice = prompt("Would you like to terminate instance %s [y/n]?" % instance.id)
    if choice.lower() != 'y':
        return
    env.ec2.terminate_instances(instance_ids=[instance.id])
    if wait_for_terminated:
        waited = 0
        while instance.state != u'terminated' and (timeout - waited > 0):
            time.sleep(wait)
            waited += wait
            instance.update()
            print "Instance %s is %s" % (instance.id, instance.state)
