import os


def create_path(instance, directory, file_type, filename):
    return os.path.join(
        directory,
        instance.id,
        file_type,
        filename
    )
