import os
import shutil
import yaml
import subprocess
from cmd_animal._logger import _create_logger
from config import global_config, docker_compose

def remove(name: str, purge: bool = False, apache_proxy: bool = True):
    """
    Remove service from list if inactive.

    :param name: service name to remove
    """
    log = _create_logger('animal_remove')

    s = str(subprocess.check_output(f'docker-compose ps {name}', shell=True), 'utf-8').split()
    if name == 'traefik' or (name in s and 'Up' in s):
        log.error('Cannot remove running service. Try to stop it first.')
        exit(1)

    # Read all services names
    try:
        services = docker_compose['services']
        services_names = [name for name, conf in services.items()]
        log.info(f'Read: {services_names} names')
    except KeyError as e:
        log.error(f'services not found in docker-compose.yml. KeyError: {e}')
        raise

    # Check is service name free to use
    if name not in services_names:
        log.error('Service with given name not exist.')
        exit(1)

    os.system(f'docker-compose rm -f {name}')

    del services[name]

    try:
        with open(global_config['docker_compose'], 'w') as fp:
            yaml.safe_dump(docker_compose, fp, default_flow_style=False)
    except FileNotFoundError as e:
        log.error(f'FileNotFoundError: {e}')
        raise
    log.info(f'Service {name} removed from config file.')

    animal_data = os.path.join(global_config['wikis_data'], name)
    # shutil.rmtree(animal_data)
    if purge:
        os.system(f'sudo rm -r {animal_data}')
        log.info(f'Removed {name} data.')
    else:
        log.info(f'Data not removed. (use --purge=True to remove data)')

    if apache_proxy:
        farmer_domain = global_config['farmer_domain']
        apache_conf_filename = f'{name}.{farmer_domain}.conf'
        os.system(f'sudo a2dissite {apache_conf_filename}')
        apache_conf_filepath = os.path.join('/etc/apache2/sites-available', apache_conf_filename)
        os.system(f'sudo rm {apache_conf_filepath}')
