
import hashlib

def hashfile(file_path, hasher=hashlib.md5(), blocksize=65536):
    """For verifying checksums of bigger files
    From: http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
    
    :param file_path: full path to file to check
    :type file_path: string or unicode
    :param hasher: hash algorithm instance, 
    :param type: e.g. hashlib.md5(), hashlib.sha256()
    :returns: checksum
    :rtype: str or unicode
    """
    if file_path is None or hasher is None: 
        return None
        
    fhandler = open(file_path, 'rb')
    
    buf = fhandler.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fhandler.read(blocksize)
    return hasher.hexdigest()