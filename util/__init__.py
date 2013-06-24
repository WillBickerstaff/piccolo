from hashlib import sha256
from random import choice
from string import ascii_letters, digits

def random_salt(length=0):
    """ Generate a random salt of letters and numbers t0 the given length."""
    if not length: length = 32
    return "".join([choice(ascii_letters+digits) for i in range(length)])

def make_hash(s, salt=None):
    """Make a SHA256 hash of the string with salt. if no salt is given
    random_salt() is called to generate one."""
    if not salt: salt = random_salt()
    return sha256(s+salt).hexdigest(), salt

def check_file(filename):
    ''' Check for a file exists, if not attempt to  empty one 

    Returns 1 if the file exists, 2 if the file had to be created
    Throws an IOError if the file does not exist and can not be created
    '''
    try: 
        open(filename, 'r').close()
        return 1
    except IOError as e:
        try:
            open(filename, 'w').close()
            return 2
        except IOError as e:
            print 'Cannot find file %s'%filename
            raise e

