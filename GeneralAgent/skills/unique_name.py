
def unique_name():
    """Generates a unique name, suitable for creating non-deletable files."""
    """Generate a unique name, suitable for creating files that won't be deleted"""
    import uuid
    return str(uuid.uuid4()).split('-')[-1]

def unique_tmp_file_name():
    """Generates a unique temporary file name which needs to be deleted afterwards."""
    """Generate a unique temporary filename that needs to be deleted afterwards"""
    import os
    tmp_dir = os.path.abspath(os.path.join(os.getcwd(), 'tmp'))
    # Create tmp_dir directory if it doesn't exist
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir + unique_name()
