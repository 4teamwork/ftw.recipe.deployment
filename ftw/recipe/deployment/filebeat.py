import os
import os.path

PROSPECTOR_TEMPLATE = """\
- type: log
  fields:
    event_type: %s
    deployment: %s
  fields_under_root: true
  json.keys_under_root: true
  json.add_error_key: true
  paths:
    - %s\
"""


def create_filebeat_conf(recipe):
    """Create a filebeat prospectors config file and return the filename of
    the created file.
    """
    default_etc_dir = os.path.join(recipe.buildout_dir, 'etc')
    etc_dir = recipe.options.get('etc-directory', default_etc_dir)

    filebeat_dir = os.path.join(etc_dir, 'filebeat.d')

    # Try to create the filebeat config directory
    if not os.path.isdir(filebeat_dir):
        try:
            os.makedirs(filebeat_dir)
        except OSError:
            return None

    # Create contentstats prospector (one per deployment)
    contentstats_log = os.path.join(
        recipe.buildout_dir, 'var/log/contentstats-json.log')
    contentstats_prospector = PROSPECTOR_TEMPLATE % (
        'contentstats', recipe.buildout_name, contentstats_log)

    # Add configuration for ftw.structlog logs (one per instance)
    prospectors = [contentstats_prospector]
    for zope_part in recipe.zope_parts:
        event_log = '%s/var/log/%s.log' % (recipe.buildout_dir, zope_part)
        event_log = recipe.buildout[zope_part].get('event-log', event_log)
        # ftw.structlog's log path is based on eventlog path
        structlog_json_log = event_log.replace('.log', '-json.log')

        structlog_prospector = PROSPECTOR_TEMPLATE % (
            'structlog', recipe.buildout_name, structlog_json_log)
        prospectors.append(structlog_prospector)

    # Create the filebeat config file
    file_name = '%s.yml' % os.path.join(filebeat_dir, recipe.buildout_name)
    filebeat_file = open(file_name, 'w')
    filebeat_file.write('\n'.join(prospectors))
    filebeat_file.close()
    return file_name
