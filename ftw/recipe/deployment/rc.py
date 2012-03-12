import os.path


def create_rc_scripts(recipe):
    """Create run-control scripts and return a list of all files that were
       created.
    """
    files = []

    rc_prefix = recipe.options.get('rc-prefix', 'rc-')
    rc_dir = recipe.options.get('rc-directory', None)
    if rc_dir is None:
        rc_dir = os.path.join(recipe.buildout_dir, 'bin')
    if not rc_dir:
        return files

    if recipe.has_supervisor:
        supervisorctl = '%s/bin/supervisorctl'  % recipe.buildout_dir
        supervisord = '%s/bin/supervisord'  % recipe.buildout_dir
        rc_filename = '%s/%ssupervisor'  % (rc_dir, rc_prefix)
        rc_file = open(rc_filename, 'w')
        rc_file.write(SUPERVISOR_RC_TEMPLATE % dict(
          supervisorctl=supervisorctl, supervisord=supervisord))
        files.append(rc_filename)
    else:
        for zope_part in recipe.zope_parts:
            zopectl = '%s/bin/%s'  % (recipe.buildout_dir, zope_part)
            rc_filename = '%s/%s%s'  % (rc_dir, rc_prefix, zope_part)
            rc_file = open(rc_filename, 'w')
            rc_file.write(ZOPE_RC_TEMPLATE % dict(zopectl=zopectl))
            files.append(rc_filename)

        for zeo_part in recipe.zeo_parts:
            zeoctl = '%s/bin/%s'  % (recipe.buildout_dir, zeo_part)
            rc_filename = '%s/%s%s'  % (rc_dir, rc_prefix, zeo_part)
            rc_file = open(rc_filename, 'w')
            rc_file.write(ZEO_RC_TEMPLATE % dict(zeoctl=zeoctl))
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
        su zope -c "$START_SCRIPT $*" </dev/null
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
        su zope -c "$START_SCRIPT $*" </dev/null
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
        su zope -c "$START_SCRIPT $*" </dev/null
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
        su zope -c "$START_SCRIPT $*" </dev/null
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
    su zope -c "$SUPERVISORD"
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
    su zope -c "$SUPERVISORCTL shutdown"
    RETVAL=$?
    if [ $RETVAL -eq 0 ]; then
        echo_success
    else
        echo_failure
    fi
    return $RETVAL
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
esac

exit $REVAL
"""