import os.path
from StringIO import StringIO


def create_logrotate_conf(recipe):
    """Create a logrotate configuration file and return the filename of the
       created file.
    """
    logrotate_dir = recipe.options.get('logrotate-directory', None)
    if logrotate_dir is None:
        logrotate_dir = os.path.join(recipe.buildout_dir,
                                     'etc', 'logrotate.d')
    if not logrotate_dir:
        return None

    logrotate_options = recipe.options.get('logrotate-options',
                                           '').split()
    logrotate_conf = StringIO()

    # Add configuration for zope parts
    for zope_part in recipe.zope_parts:
        logs = []
        event_log = '%s/var/log/%s.log' % (recipe.buildout_dir, zope_part)
        event_log = recipe.buildout[zope_part].get('event-log', event_log)
        if event_log:
            logs.append(event_log)
        z2_log = '%s/var/log/%s-Z2.log' % (recipe.buildout_dir, zope_part)
        z2_log = recipe.buildout[zope_part].get('z2-log', z2_log)
        if z2_log:
            logs.append(z2_log)
        if not logs:
            continue

        logrotate_conf.write('\n'.join(logs))
        logrotate_conf.write(' {\n')

        # logrotate options
        for opt in logrotate_options:
            logrotate_conf.write('    %s\n' % opt)

        # add reopening of logs using postrotate script
        if 'postrotate' not in logrotate_options:
            logrotate_conf.write('    sharedscripts\n')
            logrotate_conf.write('    postrotate\n')
            logrotate_conf.write('    /bin/kill -SIGUSR2 `cat %s/var/'
                                 '%s.pid` >/dev/null 2>&1\n' % (
                                 recipe.buildout_dir, zope_part))
            logrotate_conf.write('    endscript\n')

        logrotate_conf.write('}\n')

    # Add configuration for zeo part
    for zeo_part in recipe.zeo_parts:
        zeo_log = '%s/var/log/%s.log' % (recipe.buildout_dir, zeo_part)
        zeo_log = recipe.buildout[zeo_part].get('zeo-log', zeo_log)
        if not zeo_log:
            continue

        logrotate_conf.write('%s {\n' % zeo_log)

        # logrotate options
        for opt in logrotate_options:
            logrotate_conf.write('    %s\n' % opt)

        # logreopen is broken in ZODB <= 3.9.6
        # use copytruncate instead
        if 'nocopytruncate' not in logrotate_options:
            logrotate_conf.write('    copytruncate\n')

        logrotate_conf.write('}\n')

    # Create the logrotate file
    file_name = os.path.join(logrotate_dir, recipe.buildout_name)
    logrotate_file = open(file_name, 'w')
    logrotate_file.write(logrotate_conf.getvalue())
    logrotate_file.close()
    return file_name

    