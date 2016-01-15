import os
import os.path


def create_pack_script(recipe):
    """Creates a pack script for packing all storages.
    """
    # Packing needs a zeo server part
    if not recipe.zeo_parts:
        return []

    storages = []

    # Determine storages from zeo server parts
    for zeo_part in recipe.zeo_parts:
        file_storage = recipe.buildout[zeo_part].get('storage-number', '1')
        blob_storage = None
        if recipe.buildout[zeo_part].get('blob-storage', 'blobstorage'):
            blob_storage = recipe.buildout[zeo_part].get(
                'blob-storage', 'blobstorage')
            blob_storage = os.path.join(recipe.buildout_dir, 'var', blob_storage)
        storages.append((file_storage, blob_storage))

    # Determine storages from c.r.filestorage parts
    for fs_part in recipe.filestorage_parts:
        for part in recipe.buildout[fs_part].get('parts', '').split():
            file_storage = subpart_option(
                recipe.buildout, fs_part, part, 'zeo-storage',
                default='%(fs_part_name)s')
            blob_storage = None
            if subpart_option(recipe.buildout, fs_part, part, 'blob-storage'):
                blob_storage = subpart_option(
                    recipe.buildout, fs_part, part, 'blob-storage',
                    default=os.path.join('var', 'blobstorage-%(fs_part_name)s'))
                if not blob_storage.startswith(os.path.sep):
                    blob_storage = os.path.join(
                        recipe.buildout['buildout']['directory'], blob_storage)
            storages.append((file_storage, blob_storage))

    # Create script
    created_files = []
    script = "#!/bin/sh\n"
    zeopack = os.path.join(recipe.buildout_dir, 'bin', 'zeopack')
    for storage in storages:
        if storage[1]:
            script += "%(zeopack)s -S %(file_storage)s -B %(blob_storage)s\n" % dict(
                zeopack=zeopack, file_storage=storage[0], blob_storage=storage[1])
        else:
            script += "%(zeopack)s -S %(file_storage)s\n" % dict(
                zeopack=zeopack, file_storage=storage[0])
    script_path = os.path.join(recipe.buildout_dir, 'bin', 'packall')
    script_file = open(script_path, 'w')
    script_file.write(script)
    script_file.close()
    os.chmod(script_path, 0755)
    created_files.append(script_path)

    # Create symlink
    symlink_dir = recipe.options.get('packall-symlink-directory', None)
    if symlink_dir:
        # Try to create the symlink directory
        if not os.path.isdir(symlink_dir):
            try:
                os.makedirs(symlink_dir)
            except OSError:
                pass
        if os.path.isdir(symlink_dir):
            link_path = os.path.join(symlink_dir, recipe.buildout_name)
            if os.path.exists(link_path):
                os.remove(link_path)
            os.symlink(script_path, link_path)
            created_files.append(link_path)
    return created_files


def subpart_option(buildout, part, subpart, option, default=''):
    """Get an option for a filestorage subpart, falling back to the main part.
    """
    parts_to_check = ['%s_%s' % (part, subpart), part]
    val = default
    for p in parts_to_check:
        if p not in buildout:
            continue
        if option in buildout[p]:
            val = buildout[p][option]
            break

    return val % dict(fs_part_name=subpart)
