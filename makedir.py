import os
import CONFIG

def initFolders():
    subjects = CONFIG.VARIABLES['subjects']
    path = os.path.dirname(os.path.realpath(__file__))
    os.mkdir(path + '/courses')

    for dept in subjects:
        os.mkdir(path + '/courses' + '/' + dept)

