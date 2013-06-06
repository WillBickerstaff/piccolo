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
        
