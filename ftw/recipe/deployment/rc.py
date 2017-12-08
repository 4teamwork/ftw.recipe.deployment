from ftw.recipe.deployment.utils import chmod_executable
from zc.buildout.buildout import MissingOption
from zc.buildout import UserError
import os.path


def create_rc_scripts(recipe):
    """Create run-control scripts and return a list of all files that were
       created.
    """
    files = []

    startup_dir = recipe.options.get('startup-directory', None)
    shutdown_dir = recipe.options.get('shutdown-directory', None)
    rc_prefix = recipe.options.get('rc-prefix', 'rc-')
    rc_dir = recipe.options.get('rc-directory', None)
    rc_user = recipe.options.get('rc-user', 'zope')

    if startup_dir and not shutdown_dir:
        raise MissingOption("Option 'shutdown-directory' is required when "
                            "'startup-directory' is provided")
    if shutdown_dir and not startup_dir:
        raise MissingOption("Option 'startup-directory' is required when "
                            "'shutdown-directory' is provided")

    if startup_dir or shutdown_dir:
        # Try to create the startup directory
        if not os.path.isdir(startup_dir):
            try:
                os.makedirs(startup_dir)
            except OSError:
                pass
        # Try to create the shutdown directory
        if not os.path.isdir(shutdown_dir):
            try:
                os.makedirs(shutdown_dir)
            except OSError:
                pass

        if recipe.has_supervisor:
            # Create startup script
            script_path = os.path.join(startup_dir, recipe.buildout_name)
            script_file = open(script_path, 'w')
            script_file.write('#!/bin/sh\n%s/bin/supervisord\n' % recipe.buildout_dir)
            script_file.close()
            chmod_executable(script_path)
            files.append(script_path)
            # Create shutdown script
            script_path = os.path.join(shutdown_dir, recipe.buildout_name)
            script_file = open(script_path, 'w')
            script_file.write('#!/bin/sh\n%s/bin/supervisorctl shutdown\n' % recipe.buildout_dir)
            script_file.close()
            chmod_executable(script_path)
            files.append(script_path)
        else:
            raise UserError('supervisor section required with option startup_dir')

    else:
        if rc_dir is None:
            rc_dir = os.path.join(recipe.buildout_dir, 'bin')
        if not rc_dir:
            return files

        if recipe.has_supervisor:
            supervisorctl = '%s/bin/supervisorctl' % recipe.buildout_dir
            supervisord = '%s/bin/supervisord' % recipe.buildout_dir
            rc_filename = '%s/%ssupervisor' % (rc_dir, rc_prefix)
            rc_file = open(rc_filename, 'w')
            rc_file.write(SUPERVISOR_RC_TEMPLATE % dict(
                supervisorctl=supervisorctl, supervisord=supervisord, user=rc_user))
            rc_file.close()
            chmod_executable(rc_filename)
            files.append(rc_filename)
        else:
            for zope_part in recipe.zope_parts:
                zopectl = '%s/bin/%s' % (recipe.buildout_dir, zope_part)
                rc_filename = '%s/%s%s' % (rc_dir, rc_prefix, zope_part)
                rc_file = open(rc_filename, 'w')
                rc_file.write(ZOPE_RC_TEMPLATE % dict(zopectl=zopectl, user=rc_user))
                rc_file.close()
                chmod_executable(rc_filename)
                files.append(rc_filename)

            for zeo_part in recipe.zeo_parts:
                zeoctl = '%s/bin/%s' % (recipe.buildout_dir, zeo_part)
                rc_filename = '%s/%s%s' % (rc_dir, rc_prefix, zeo_part)
                rc_file = open(rc_filename, 'w')
                rc_file.write(ZEO_RC_TEMPLATE % dict(zeoctl=zeoctl, user=rc_user))
                rc_file.close()
                chmod_executable(rc_filename)
                files.append(rc_filename)

    return files


ZOPE_RC_TEMPLATE = """#!/bin/sh

# chkconfig: 345 90 10
# description: Starts Zope

START_SCRIPT="%(zopectl)s"

[ -f $START_SCRIPT ] || exit 1

# Source function library.
. /etc/init.d/functions

RETVAL=0

if [ $(whoami) != "root" ]; then
    echo "You must be root."
    exit 1
fi

case $1 in
    start|stop)
        su %(user)s -c "$START_SCRIPT $*" </dev/null
        RETVAL=$?
        if [ $RETVAL -eq 0 ]
        then
            echo_success
        else
            echo_failure
        fi
        echo
        ;;
    restart)
        ${0} stop
        sleep 1
        ${0} start
        ;;
    *)
        su %(user)s -c "$START_SCRIPT $*" </dev/null
        ;;
esac
"""

ZEO_RC_TEMPLATE = """#!/bin/sh

# chkconfig: 345 85 15
# description: Starts ZEO server

START_SCRIPT="%(zeoctl)s"

[ -f $START_SCRIPT ] || exit 1

# Source function library.
. /etc/init.d/functions

RETVAL=0

if [ $(whoami) != "root" ]; then
    echo "You must be root."
    exit 1
fi

case $1 in
    start|stop)
        su %(user)s -c "$START_SCRIPT $*" </dev/null
        RETVAL=$?
        if [ $RETVAL -eq 0 ]
        then
            echo_success
        else
            echo_failure
        fi
        echo
        ;;
    restart)
        ${0} stop
        sleep 1
        ${0} start
        ;;
    *)
        su %(user)s -c "$START_SCRIPT $*" </dev/null
        ;;
esac
"""

SUPERVISOR_RC_TEMPLATE = """#!/bin/sh

# chkconfig: 345 90 10
# description: Starts supervisor

SUPERVISORCTL="%(supervisorctl)s"
SUPERVISORD="%(supervisord)s"

[ -f $SUPERVISORD ] || exit 1
[ -f $SUPERVISORCTL ] || exit 1

# Source function library.
. /etc/init.d/functions

RETVAL=0

if [ $(whoami) != "root" ]; then
    echo "You must be root."
    exit 1
fi

start() {
    echo -n "Starting supervisor: "
    su %(user)s -c "$SUPERVISORD"
    RETVAL=$?
    if [ $RETVAL -eq 0 ]; then
        echo_success
    else
        echo_failure
    fi
    return $RETVAL
}

stop() {
    echo -n "Stopping supervisor: "
    su %(user)s -c "$SUPERVISORCTL shutdown"
    RETVAL=$?
    if [ $RETVAL -eq 0 ]; then
        echo_success
    else
        echo_failure
    fi
    return $RETVAL
}

status() {
    su %(user)s -c "$SUPERVISORCTL status"
}

case "$1" in
    start)
        start
        ;;

    stop)
        stop
        ;;

    restart)
        stop
        start
        ;;

    status)
        status
        ;;
esac

exit $REVAL
"""
