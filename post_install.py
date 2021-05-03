# post install script
import os
import shutil
import sys

if __name__ == "__main__":
    args = sys.argv[1:]

    user_dir=os.path.expanduser('~/tablePackager')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if not os.path.exists(user_dir+'/database'):
        os.makedirs(user_dir+'/database')
    shutil.copyfile('lib/packager/database/manufacturer.json',user_dir+'/database/manufacturer.json')

    if os.path.exists(user_dir+'/database/pinball_machines.json'):
        shutil.copyfile(user_dir+'/database/pinball_machines.json', user_dir+'/database/pinball_machines.json.backup')
    shutil.copyfile('lib/packager/database/pinball_machines.json', user_dir + '/database/pinball_machines.json')

    
