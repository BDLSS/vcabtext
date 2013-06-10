#!/usr/bin/env python
# encoding: utf-8
"""This module has commands for dealing with the setup of Django projects."""
import logging
import sys
import optparse
import os
import subprocess 
import shutil
import datetime

DEBUG = True

class DjAdmin(object):
    '''Perform admin tasks on a django system.'''
    def __init__(self, user, group, git_dj, git_out='Not currently used',
                 rootdir='/opt', djdir='oxproject', outdir='oxstore',
                 mediadir='oxmedia', dbname='data.sq3'):
        '''Setup the system options tasks make use of.'''
        self.DEFAULT_USER = user # The owner of the folders. eg vocabadmin
        self.DEFAULT_GROUP = group # The group who need access. eg. wwwdata
        self.GIT_DJANGO = git_dj # A repository that contains the main system.
        self.GIT_OUTSIDE = git_out # Repository for other stuff, like templates.
        self.DIR_ROOT = rootdir # Where everything gets put.
        self.DIR_DJANGO = os.path.join(self.DIR_ROOT,djdir) # Main system here.
        self.DIR_OUTSIDE = os.path.join(self.DIR_ROOT,outdir) # Other stuff.
        self.DIR_MEDIA = os.path.join(self.DIR_ROOT, mediadir) # Upload folder.
        self.DB_FILE = os.path.join(self.DIR_OUTSIDE, dbname) # Sqlite3 db.
        
        usr_share_pyshared_dj = "ln_contrib_admin_media"
        self.DIR_LINKS = os.path.join(self.DIR_OUTSIDE, usr_share_pyshared_dj)
        self.DIR_CONTRIB = '/usr/share/pyshared/django/contrib/admin'
        
        self.OPTIONS = optparse.OptionParser()
        self.setup_options()
        
    def setup_options(self):
        '''Returns a list of commands available and enables OptionParser.'''
        #self.OPTIONS.set_usage('Usage: sudo vadmin-py [option]')
        des = 'Does admin tasks on a django system.'
        epi = 'You need to use sudo or have write access to:  %s'%self.DIR_ROOT
        self.OPTIONS.set_description(des)
        self.OPTIONS.epilog = epi
        
        items = {
        'mkdirs':('m','Make the folders need for the application.'),
        'chown':('c','Change the user and group ownership for the folders.'),
        'rmdb':('r','Removes the local development database.'),
        'wipe':('w','Wipe project folders (rm -rf) , not logs.'),
        'pull':('p','Pull the current master branch into server.'),
        'esys':('e', 'Enables the system folder, (eg. templates'),
        'setup':('s','Setup up the server (Does m, c and p in sequence.)'),
        'reset':('N','Resets the server (Does w then m, c and p)'),
        'fdesk':('f', 'Fixes ownership rights on development desktops.'),
        'Get': ('g', 'Get the latest version of this script.'),
                 }
                 
        for item in items:
            brief = '-%s'%items[item][0]
            full = '--%s'%item
            note = items[item][1]
            self.OPTIONS.add_option(brief, full , help=note, default=False,
                        dest='%s'%item, action='store_true')
        return items
            
    def do_tasks(self, argv=None):
        '''Perform the relevant task(s) for the command line option given.''' 
        if len(argv) == 1: # No command line options given, so add help option.
            sys.argv.append("-h")
        (opts, unused) = self.OPTIONS.parse_args(argv)
        if opts.mkdirs: self.do_mkdirs()
        if opts.chown: self.do_chown()
        if opts.rmdb: self.do_rmdb()
        if opts.wipe: self.do_wipe()
        if opts.pull: self.do_pull()
        if opts.esys: self.do_esys()
        if opts.setup: self.do_setup()
        if opts.reset: self.do_reset()
        if opts.fdesk: self.do_desktop()
        if opts.get: self.do_get()
    
    def do_command(self, command):
        '''Run the command tuple on the OS command line.'''
        p = subprocess.Popen(command, stdin = subprocess.PIPE, 
                          stdout = subprocess.PIPE, close_fds = True)
        answer = p.stdout
        return answer.readlines()
    
    def list(self, prefix, folder=None, compare=None):
        '''Returns a listing of folder with a prefix label, compare 2 runs.'''
        if not folder: folder = self.DIR_ROOT
        items = os.listdir(folder)
        logging.info('%s - %s'%(prefix, items))
        if compare==items: logging.info('No changes were made.')
        return items # this value might be compared on a second run
        
    def list_long(self, cause, folder=None):
        '''Runs ls -l on folder and logs each line with prefix.'''
        if not folder: folder = self.DIR_ROOT
        command = ['ls', '-l', folder]
        items = self.do_command(command)
        for item in items:
            logging.debug('%s : %s'%(cause, str(item).strip()))

    def when(self):
        '''Get a string with date and time, for use in filename.'''
        when = str(datetime.datetime.now())
        checks = [' ', ':', '.']
        for check in checks:
            when = when.replace(check, '-')
        return when
        
    # ------------------------------------------------------------
    # Methods that get run depending on the commmand line options.
    # ------------------------------------------------------------                
    def do_mkdirs(self):
        logging.warn('Making folders needed.')
        before = self.list('before')
        
        # Setup and/or check the django project folder
        try:
            os.makedirs(self.DIR_DJANGO)
        except OSError, e:
            logging.debug(e)
        if not os.path.exists(self.DIR_DJANGO):
            logging.critical('Cannot find django folder, did you run as sudo?')            
            
        # Setup and/or check the outside folder
        try:
            os.makedirs(self.DIR_OUTSIDE)
        except OSError, e:
            logging.debug(e)
        if not os.path.exists(self.DIR_OUTSIDE):
            logging.critical('Cannot find outside folder, did you run as sudo?')

        # Setup and/or check the media folder
        try:
            os.makedirs(self.DIR_MEDIA)
        except OSError, e:
            logging.debug(e)
        if not os.path.exists(self.DIR_MEDIA):
            logging.critical('Cannot find media folder, did you run as sudo?')
            
        self.list('after', compare=before)    
        
        # Setup and/or check the folder that store links
        try:
            os.makedirs(self.DIR_LINKS)
        except OSError, e:
            logging.debug(e)
        if not os.path.exists(self.DIR_LINKS):
            logging.critical('Cannot find link folder, did you run as sudo?')
            
    def get_usergroup(self, ask_admin=True):
        '''Returns the user and group to use with option to customise defaults.'''
        user = group = ''
        if ask_admin:
            user = raw_input(
        'Username to use, press enter for default. [%s] > '%self.DEFAULT_USER)
            group = raw_input(
        'Groupname to use, press enter for default. [%s] > '%self.DEFAULT_GROUP)
        if not user:
            user = self.DEFAULT_USER
        if not group:
            group = self.DEFAULT_GROUP
        using = '%s:%s'%(user, group)
        logging.info('The user:group being used is: %s'%using)
        logging.info('If user does not exist use: sudo useradd <%s>'%self.DEFAULT_USER)
        return using
        
    def do_chown(self, ask_admin=True):
        logging.warn('Changing user and group ownership')
        usergroup = self.get_usergroup(ask_admin)
        self.list_long('chown-before')
        subprocess.call(['chown', '-R', usergroup, self.DIR_DJANGO])
        subprocess.call(['chown', '-R', usergroup, self.DIR_OUTSIDE])
        subprocess.call(['chown', '-R', usergroup, self.DIR_MEDIA])
        self.list_long('chown-after')
        
    def do_rmdb(self):
        logging.warn('Removing development database')
        try:
            os.remove(self.DB_FILE)
        except OSError, e:
            logging.debug(e)
        if os.path.exists(self.DB_FILE):
            logging.critical('Unable to remove the development database file.')
            
    def do_wipe(self):
        logging.critical('Wiping the vocab server.')
        before = self.list('before')     
        self.list_long('wipe-before')
        subprocess.call(['rm', '-rf', self.DIR_DJANGO])
        subprocess.call(['rm', '-rf', self.DIR_OUTSIDE])
        subprocess.call(['rm', '-rf', self.DIR_MEDIA])
        self.list_long('wipe-after')
        self.list('after',compare=before)    
    
    # ------------------------------------------------------------
    # Methods that sync local system to git items.
    # ------------------------------------------------------------           
    def _sync(self, internal_dir, git_path):
        os.chdir(internal_dir)
        current = os.path.join(internal_dir, 'current')
        backup = os.path.join(internal_dir, 'zbefore-%s'%self.when())
        if os.path.exists(current):
            shutil.move(current, backup)
        self.do_command(['git', 'init'])
        self.do_command(['git', 'clone', git_path, 'current'])
    
    def do_pull(self):
        logging.warn('Pulling the current master branch.')
        self._sync(self.DIR_DJANGO, self.GIT_DJANGO)
            
    def do_esys(self):
        logging.warn('Enabling and syncing the non-django system folders.')
        #self._sync(self.DIR_OUTSIDE, self.GIT_OUTSIDE)
        for item in ['css', 'img', 'js']:
            folderfrom = os.path.join(self.DIR_CONTRIB, item)
            folderto = os.path.join(self.DIR_LINKS, item)
            self.do_command(['ln', '-s', folderfrom, folderto])

    # ------------------------------------------------------------
    # Meta tasks that sequence togother the tasks above.
    # ------------------------------------------------------------               
    def do_setup(self):
        logging.warn('Setting up the dj system from scratch.')
        self.do_mkdirs()
        self.do_pull()
        self.do_esys()
        self.do_chown(False)
        logging.info("Don't forget to fix desktop (-f) on development desktops.")
        
    def do_reset(self):
        logging.critical('Reseting the dj system')
        self.do_wipe()
        self.do_mkdirs()
        self.do_pull()
        self.do_esys()
        self.do_chown(False)
        logging.info("Don't forget to fix desktop (-f) on development desktops.")
    
    # ------------------------------------------------------------
    # Other tasks that can get done.
    # ------------------------------------------------------------       
    def do_desktop(self):
        logging.critical('Doing fixes required for development desktops.')
        name = raw_input('Type username who needs write access.  ')
        if name:
            self.DEFAULT_USER = name
            self.DEFAULT_GROUP = name
            self.do_chown(False)
    
    def do_get(self):
        logging.critical('Attempting to get the latest script.'
        self.do_command(['wget', 'https://github.com/bdlss/vcabtext/raw/master/djsetup.py'])
        
if __name__ == '__main__':
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    ug = 'vocabadmin'
    master='git://github.com/BDLSS/vcabtext.git'
    a = DjAdmin(ug, ug, master)
    argv = sys.argv 
    
    #argv.append('-f') # this will let you fake a command line option
    a.do_tasks(argv)
    