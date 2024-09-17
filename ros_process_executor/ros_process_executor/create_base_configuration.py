import datetime
import json
import os
import shutil
from typing import Optional

from pathlib import Path



# ToDO: This makes a lot of sense as an object.
def create_base_configuration(counter) -> str:
    str_counter = "" if counter == -1 else str(counter)
    destination = f'/home/kpsruser/kpe-ros2-core/tests/config/my_config{str_counter}.json'
    with open(destination, 'r') as f:
        environment_file = json.load(f)
    
    url_stat = environment_file["StringProperties"]['stat_filename']
    url_policy = environment_file["StringProperties"]['streaming_conf_file']
    
    environment_file["StringProperties"]['log_filename'] = \
        '/'.join(environment_file["StringProperties"]['log_filename'].split('/')[:-1]+[f'log{counter+1}.log'])
    
    environment_file["StringProperties"]['stat_filename'] = \
        '/'.join(environment_file["StringProperties"]['stat_filename'].split('/')[:-1]+[f'stat{counter+1}.csv'])
    
    environment_file["StringProperties"]['streaming_conf_file'] = \
        '/'.join(environment_file["StringProperties"]['streaming_conf_file'].split('/')[:-1]+[f'streaming_policy{counter+1}.json'])

    environment_file["BoolProperties"]['export_streaming_configuration'] = False
    environment_file["BoolProperties"]['use_default_streaming_factory'] = False
    
    config_for_ros_location = f'/home/kpsruser/kpe-ros2-core/tests/config/my_config{counter+1}.json'
    with open(config_for_ros_location, "w+") as conf_file:
        json.dump(environment_file, conf_file, indent=2, sort_keys=True)



    

    return config_for_ros_location, url_stat, url_policy
if __name__ == '__main__':
    create_base_configuration()