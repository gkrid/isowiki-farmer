import os
import shutil

import yaml

if not os.path.isfile('./config.local.yml'):
    shutil.copyfile('./config.yml', './config.local.yml')

with open('./config.local.yml', 'r') as fp:
    global_config = yaml.safe_load(fp)

if not os.path.isfile(global_config['docker_compose']):
    with open(global_config['docker_compose'], 'w') as fp:
        docker_compose = {'services': {}, 'version': '3.3'}
        yaml.safe_dump(docker_compose, fp, default_flow_style=False)
else:
    with open(global_config['docker_compose'], 'r') as fp:
        docker_compose = yaml.safe_load(fp)

# if not os.path.isdir('./engine_config.local'):
#     shutil.copytree('./engine_config', './engine_config.local')