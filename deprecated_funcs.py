



def get_extensions():
    #helper function for remove_duplicates_files
    #Temporary, should be removed later.
    #Unused
    extensions = []
    for f in Raw_File_List:
        #if extensions doesn't contain the extension of f
        if f.split('.')[-1] not in extensions:
            extensions.append(f.split('.')[-1])
    return extensions
#DEPRECATED move files into folders, takes file_dict(category:filepath) as an argument
def move_files(file_dict):
    #TODO status messages for real run 
    #TODO TEST!!! 
    if _dry_run_only:
        print('DRY RUN ONLY, NO FILES WILL BE MOVED.')
        #print which folders will be created
        #and which files go in which folders
        for key, value in file_dict.items():
            print(f'moving {len(value)} file(s) to {key}...')
            for file in value:
                print(f'\t{file.split("/")[-1]}...')
        print('Dry run complete, no files moved.')
        #stop function
        return
    #print status
    print(f'moving {get_value_count_from_dictionary(file_dict)} files...')
    # create folders
    create_folders(file_dict)
    # iterate through file_dict
    files_moved = 0
    for file_category, file_list in file_dict.items():
        # iterate through files in value
        print(f'moving {len(file_list)} file(s) to {file_category}...')
        for file in file_list:
            # check if file exists
            if os.path.exists(f'{file}'):
                # if so, move file to folder
                print(f'\tmoving {file}...')
                #if target folder exists
                if os.path.exists(f'{Target_Directory}/{file_category}'):
                    #move file
                    shutil.move(f'{file}', f'{Target_Directory}/{file_category}/{file}')
                    files_moved += 1
                else:
                    #print error message
                    print(f'\t{Target_Directory}/{file_category} does not exist, skipping...')
    print(f'{files_moved} files moved.')

#DEPRECATED move files into archives, takes file_dict(category:filepath) as an argument
def archive_files(file_dict):
    #Test test test.  Completely untested
    if _dry_run_only:
        print('DRY RUN ONLY, NO FILES WILL BE ARCHIVED.')
        #print which folders will be created
        #and which files go in which folders
        files_archived = 0
        for key, value in file_dict.items():
            print(f'zipping {len(value)} file(s) to {key}.zip...')
            for file in value:
                print(f'\t{file.split("/")[-1]}...')
                files_archived += 1
        print(f'Dry run complete, {files_archived} file(s) archived.')
        #stop function
        return
    #print status
    print(f'archiving {get_value_count_from_dictionary(file_dict)} file(s)...')
    # create folders
    create_archives(file_dict)
    # iterate through file_dict
    files_archived = 0
    for file_category, file_list in file_dict.items():
        # iterate through files in value
        print(f'archiving {len(file_list)} file(s) to {file_category}.zip...')
        for file in file_list:
            # check if file exists
            if os.path.exists(f'{file}'):
                # if so, move file to folder
                print(f'\tarchiving {file}...')
                if os.path.exists(f'{Target_Directory}/{file_category}.zip'):
                    with zipfile.ZipFile(f'{Target_Directory}/{file_category}.zip', 'a') as zip:
                        #remove absolutepath from filename before zipping
                        zip.write(f'{file}', arcname=f'{file.split("/")[-1]}')
                        #remove original file
                        os.remove(f'{file}')
                        #zip.write(f'{file}')
                    files_archived += 1
                else:
                    print(f'\t{Target_Directory}/{file_category}.zip does not exist, skipping...')
    print(f'{files_archived} files archived.')

Extensions_Dictionary = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'psd', 'raw', 'heif', 'indd', 'ai', 'eps', 'ps', 'webp'],
    'audio': ['aac', 'aa', 'dvf', 'm4a', 'm4b', 'm4p', 'mp3', 'msv', 'ogg', 'oga', 'raw', 'vox', 'wav', 'wma'],
    'videos': ['3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob', 'wmv'],
    'documents': ['doc', 'docx', 'odt', 'pdf', 'rtf', 'tex', 'txt', 'wks', 'wps', 'wpd', 'csv', 'dat', 'pps', 'ppt', 'pptx', 'ods', 'xls', 'xlsx'],
    'executables': ['apk', 'bat', 'bin', 'cgi', 'pl', 'com', 'exe', 'gadget', 'jar', 'wsf'],
    'archives': ['7z', 'arj', 'pkg', 'rar', 'z', 'zip'],
    'disc_images': ['bin', 'dmg', 'iso', 'toast', 'vcd'],
    'data': ['csv', 'dat', 'db', 'dbf', 'log', 'mdb', 'sav', 'sql', 'tar', 'xml'],
    'internet': ['asp', 'aspx', 'cer', 'cfm', 'cgi', 'pl', 'css', 'htm', 'html', 'js', 'jsp', 'part', 'php', 'py', 'rss', 'xhtml'],
    'programming': ['c', 'class', 'cpp', 'cs', 'h', 'java', 'sh', 'swift', 'vb', 'py', 'pyc', 'pyo', 'pyd', 'pyw', 'pyz', 'py3', 'pyc3', 'pyo3', 'pyd3', 'pyw3', 'pyz3', 'py2', 'pyc2', 'pyo2', 'pyd2', 'pyw2', 'pyz2'],
    'system': ['bak', 'cab', 'cfg', 'cpl', 'cur', 'dll', 'dmp', 'drv', 'icns', 'ico', 'ini', 'lnk', 'msi', 'sys', 'tmp'],
    'misc': ['crdownload', 'crx', 'plugin', 'torrent'],
    'Linux': ['deb', 'rpm', 'tar.gz', 'tar.xz', 'tar.bz2', 'tar', 'appimage', 'yay', 'pacman', 'snap', 'flatpak'],
    'Windows': ['exe', 'msi', 'msix', 'msixbundle', 'msu', 'msp', 'appx', 'appxbundle', 'appxupload', 'appinstaller', 'bat', 'cmd', 'ps1', 'psm1', 'psd1', 'ps1xml', 'psc1', 'psrc', 'reg', 'inf', 'url', 'lnk', 'inf', 'url', 'lnk'],
    'models': ['3ds', '3mf', 'blend', 'fbx', 'gltf', 'obj', 'stl', 'dae', 'dxf', 'lwo', 'lws', 'lxo', 'ma', 'max', 'mb', 'mesh', 'mesh.xml', 'obj', 'ply', 'skp', 'wrl', 'x', 'x3d', 'x3db', 'x3dv', 'xgl', 'zgl']
}