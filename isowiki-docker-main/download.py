#!/usr/bin/env python3
import json
import shutil
import urllib.request
import os
import subprocess
import glob

default_plugins = ['advanced', 'alphalist2', 'approve', 'backlinks', 'bez', 'bureaucracy', 'button', 'discussion',
                   'dropfiles', 'edittable', 'filelisting', 'flowcharts', 'folded', 'fontcolor', 'googledrawing',
                   'icons', 'iframe', 'include', 'indexmenu', 'ireadit', 'move', 'nosidebar', 'notification',
                   'numberof', 'pagemod', 'pdfjs', 'smtp', 'sqlite', 'struct', 'structat', 'structcombolookup',
                   'structgantt', 'structgroup', 'structinputstretch', 'structjoin', 'structnotification', 'structodt',
                   'structrowcolor', 'structsection', 'structstatus', 'subnumberlist', 'tablecalc', 'tablelayout',
                   'telleveryone', 'templatepagename', 'toctweak', 'translation', 'wrap']

manual_plugins = {'isowikitweaks': 'https://github.com/gkrid/dokuwiki-plugin-isowikitweaks/archive/master.zip',
                  'redirect': 'https://github.com/gkrid/dokuwiki-plugin-redirect/archive/master.zip',
                  'simplenavi': 'https://github.com/solewniczak/simplenavi/archive/skipns.zip'}

if not os.path.isdir('./engine_config.local'):
    shutil.copytree('./engine_config', './engine_config.local')

engines_dir = './core_engines'

# current_dir = sys.path[0]
# engines_dir = os.path.join(current_dir, "core_engines")
# engines_dir = global_config['core_engines']
archive_filepath = os.path.join(engines_dir, "dokuwiki-stable.tgz")
command = f"wget -P {engines_dir} https://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz"
subprocess.run(command, shell=True)
dokuwiki_path = os.path.join(engines_dir, "dokuwiki-stable.tgz")

command = f"tar -ztf {dokuwiki_path}|head -n1"
proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
dw_version = proc.stdout.decode("utf-8").strip().rstrip('/')
dw_filepath = os.path.join(engines_dir, dw_version)

engines = glob.glob(os.path.join(engines_dir, dw_version + '.*'))
engines = [os.path.basename(engine_path) for engine_path in engines]

if len(engines) == 0:
    engine_build = 0
else:
    last_engine = max(engines)
    last_engine_split = last_engine.split('.')
    last_engine_build = last_engine_split[1]
    engine_build = int(last_engine_build) + 1

engine_filename= f"{dw_version}.{engine_build:03}"
engine_filepath = os.path.join(engines_dir, engine_filename)
print(f"Creating new engine: {engine_filename}")

command = f"tar -zxf {archive_filepath} -C {engines_dir} && mv {dw_filepath} {engine_filepath} && rm {archive_filepath}"
subprocess.run(command, shell=True)

latest_sym_link = os.path.join(engines_dir, "latest")
command = f"rm {latest_sym_link} ; ln -s {engine_filename} {latest_sym_link}"
subprocess.run(command, shell=True)


EXTENSION_REPOSITORY_API = 'http://www.dokuwiki.org/lib/plugins/pluginrepo/api.php'
all_extensions = json.load(urllib.request.urlopen(EXTENSION_REPOSITORY_API))
extensions_dict = {extension['plugin']: extension for extension in all_extensions}
extensions_dir = os.path.join(engine_filepath, 'lib/plugins')

# download plugins
def download_plugin(name, download_url=''):
    if download_url == '':
        if not name in extensions_dict:
            print(f'unknown plugin {name}')
            return
        print(f'downloading plugin {name} ...', end=' ')
        extension = extensions_dict[name]
        download_url = extension['downloadurl']
    else:
        print(f'downloading plugin {name} from {download_url} ...', end=' ')

    extension_archive_filepath = os.path.join(extensions_dir, f'{name}-archive')
    command = f"wget -P {engines_dir} {download_url} -O {extension_archive_filepath}"
    subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)

    command = f"file -ib {extension_archive_filepath}"
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    mime = proc.stdout.decode("utf-8").split(';')[0].strip()

    if mime == 'application/zip':
        command_get_content = 'zipinfo -1 {archive}'
        command_extract = 'unzip {archive} -d {destination}'
    elif mime == 'application/gzip':
        command_get_content = 'tar -ztf {archive}'
        command_extract = 'tar -zxf {archive} -C {destination}'
    else:
        print(f'unknown mime type: {mime}')
        command = f"rm {extension_archive_filepath}"
        subprocess.run(command, shell=True)
        return
    # get extension main folder
    command = command_get_content.format(archive=extension_archive_filepath) + " | head -n1"
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    extension_maindir_filename = proc.stdout.decode("utf-8").strip().rstrip('/')
    extension_maindir_filepath = os.path.join(extensions_dir, extension_maindir_filename)
    extension_newdir_filepath = os.path.join(extensions_dir, name)

    command = command_extract.format(archive=extension_archive_filepath, destination=extensions_dir)+\
              f" && mv {extension_maindir_filepath} {extension_newdir_filepath} && rm {extension_archive_filepath}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)
    print('ok')


for plugin in default_plugins:
    download_plugin(plugin)

for plugin, url in manual_plugins.items():
    download_plugin(plugin, url)

# fill with default configuration
# engine_conf = os.path.join(engine_filepath, 'conf/')
# command = f"cp engine_config.local/* {engine_conf}"
# subprocess.run(command, shell=True)

command = f"cp .htaccess {engine_filepath}"
subprocess.run(command, shell=True)