import glob
import os
import yaml
from cmd_animal._logger import _create_logger
from distutils.dir_util import copy_tree
from config import global_config, docker_compose

def create(name: str, apache_proxy: bool = True):
    """
    Create wiki with separated data, running on given engine.

    :param name: service name to create
    :param engine: if given engine does not exist - use default version.
    """

    log = _create_logger('animal_create')
    doku_name = name

    # Read all services names
    try:
        services = docker_compose['services']
        services_names = [name for name, conf in services.items()]
        services_ports_mappings = [conf['ports'][0] for name, conf in services.items()]
        service_host_ports = [int(port_mapping.split(':')[0]) for port_mapping in services_ports_mappings]
        if len(service_host_ports) == 0:
            service_host_port = 8000
        else:
            service_host_port = max(service_host_ports) + 1
        log.info(f'Services in config: {services_names}')
    except KeyError as e:
        log.error('services not found in docker-compose.yml. KeyError: {0}'.format(e))
        raise

    # Check is service name free to use
    if doku_name in services_names:
        log.error('Service with given name is already created. '
                  'Change service name or use update to update given service')
        exit(1)

    # define new service
    services[doku_name] = {}
    # ENGINE_PATH = os.path.join(global_config['core_engines'], version)
    # services[doku_name]['build'] = {
    #     'context': '.',
    #     'args': {
    #         'ENGINE_PATH': ENGINE_PATH
    #     }
    # }
    # services[doku_name]['build'] = f'.'
    # services[doku_name]['build'] = {
    #     'context': '.',
    #     'dockerfile': f'Dockerfile.{enviroment}'
    # }
    services[doku_name]['image'] = 'gkrid/isowiki'
    services[doku_name]['container_name'] = doku_name
    # services[doku_name]['environment'] = {}
    # services[doku_name]['environment']['engine_version'] = version

    # add labels
    # labels = [
    #     "traefik.enable=true",
    #     "traefik.http.routers.{0}.rule=Host(`{0}.localhost`)".format(doku_name),
    #     "traefik.http.routers.{0}.entrypoints=web".format(doku_name),
    # ]
    # services[doku_name]['labels'] = labels

    # add volumes if not exists
    # version = 'latest'
    # core_engines_conf = os.path.join(global_config['core_engines'], version, 'conf')
    # core_engines_data = os.path.join(global_config['core_engines'], version, 'data')

    # wikis_data = os.path.join(global_config['wikis_data'], doku_name)
    # wikis_data_conf = os.path.join(wikis_data, 'conf')
    # wikis_data_data = os.path.join(wikis_data, 'data')
    # if os.path.exists(wikis_data):
    #     log.info(f'Data folder: {wikis_data} exists. New data files are not copied.')
    # else:
    #     # https://github.com/gkrid/isowiki-docker/archive/main.tar.gz
    #     os.system(f'wget -P /tmp https://github.com/gkrid/isowiki-docker/archive/main.tar.gz && tar -xzf /tmp/main.tar.gz')
    #     copy_tree('/tmp/isowiki-docker-main/files/conf', wikis_data_conf)
    #     copy_tree('/tmp/isowiki-docker-main/files/data', wikis_data_data)
    #     # correct rights
    #     os.system(f'sudo chown -R www-data:www-data {wikis_data_conf}')
    #     os.system(f'sudo chown -R www-data:www-data {wikis_data_data}')

    # engine_path = os.path.join(global_config['core_engines'], version)
    # volumes = []
    # if enviroment == 'dev':
    #     engine_path = os.path.join(global_config['core_engines'], version)
    #     volumes.append(f'{engine_path}:/var/www/html:ro')

    # volumes.append(f'{wikis_data_conf}:/var/www/html/conf:rw')
    # volumes.append(f'{wikis_data_data}:/var/www/html/data:rw')

    wikis_data = os.path.join(global_config['wikis_data'], doku_name)
    volumes = [
        f'{wikis_data}:/isowiki:rw',
    ]


    services[doku_name]['ports'] = [f'{service_host_port}:80']
    services[doku_name]['volumes'] = volumes

    try:
        with open(global_config['docker_compose'], 'w') as fp:
            yaml.safe_dump(docker_compose, fp, default_flow_style=False)
    except FileNotFoundError as e:
        log.error("FileNotFoundError: ", e)
        raise

    log.info(f'Created {doku_name} service port: {service_host_port}.')

    if apache_proxy:
        with open(global_config['apache_conf_tpl'], 'r') as fp:
            apache_conf = fp.read()\
                .replace('$(animal_name)', doku_name)\
                .replace('$(farmer_domain)', global_config['farmer_domain']) \
                .replace('$(ssl_include)', global_config['ssl_include']) \
                .replace('$(ssl_certificate_file)', global_config['ssl_certificate_file']) \
                .replace('$(ssl_certificate_key_file)', global_config['ssl_certificate_key_file']) \
                .replace('$(port)', str(service_host_port))
        farmer_domain = global_config['farmer_domain']
        apache_conf_filename = f'{doku_name}.{farmer_domain}.conf'
        with open(f'/tmp/{apache_conf_filename}', 'w') as fp:
            fp.write(apache_conf)
        apache_conf_filepath = os.path.join('/etc/apache2/sites-available', apache_conf_filename)
        os.system(f'sudo mv /tmp/{apache_conf_filename} {apache_conf_filepath}')
        os.system(f'sudo a2ensite {apache_conf_filename}')
        # os.system(f'sudo systemctl reload apache2')
