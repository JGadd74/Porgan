import argparse
import os,fnmatch
from pathlib import Path
import zipfile
import shutil
import re

#Why the fuck are these all different dictionaries? this is over fucking complicated.
#What the fuck was I thinking

# file extensions dictionaries
images = {'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'psd', 'raw', 'heif', 'indd', 'ai', 'eps', 'ps', 'webp']}
audio = {'audio': ['aac', 'aa', 'dvf', 'm4a', 'm4b', 'm4p', 'mp3', 'msv', 'ogg', 'oga', 'raw', 'vox', 'wav', 'wma']}
video = {'video': ['3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob', 'wmv']}
documents = {'documents': ['doc', 'docx', 'odt', 'pdf', 'rtf', 'tex', 'txt', 'wks', 'wps', 'wpd', 'csv', 'dat', 'pps', 'ppt', 'pptx', 'ods', 'xls', 'xlsx']}
executables = {'executables': ['apk', 'bat', 'bin', 'cgi', 'pl', 'com', 'exe', 'gadget', 'jar', 'wsf']}
archives = {'archives': ['7z', 'arj', 'pkg', 'rar', 'z', 'zip']}
disc_images = {'disc_images': ['bin', 'dmg', 'iso', 'toast', 'vcd']}
data = {'data': ['csv', 'dat', 'db', 'dbf', 'log', 'mdb', 'sav', 'sql', 'tar', 'xml']}
internet = {'internet': ['asp', 'aspx', 'cer', 'cfm', 'cgi', 'pl', 'css', 'htm', 'html', 'js', 'jsp', 'part', 'php', 'py', 'rss', 'xhtml']}
programming = {'programming': ['c', 'class', 'cpp', 'cs', 'h', 'java', 'sh', 'swift', 'vb', 'py', 'pyc', 'pyo', 'pyd', 'pyw', 'pyz', 'py3', 'pyc3', 'pyo3', 'pyd3', 'pyw3', 'pyz3', 'py2', 'pyc2', 'pyo2', 'pyd2', 'pyw2', 'pyz2']}
system = {'system': ['bak', 'cab', 'cfg', 'cpl', 'cur', 'dll', 'dmp', 'drv', 'icns', 'ico', 'ini', 'lnk', 'msi', 'sys', 'tmp']}
misc = {'misc': ['crdownload', 'crx', 'plugin', 'torrent']}
Linux = {'Linux': ['deb', 'rpm', 'tar.gz', 'tar.xz', 'tar.bz2', 'tar', 'appimage', 'yay', 'pacman', 'snap', 'flatpak']}
Windows = {'Windows': ['exe', 'msi', 'msix', 'msixbundle', 'msu', 'msp', 'appx', 'appxbundle', 'appxupload', 'appinstaller', 'bat', 'cmd', 'ps1', 'psm1', 'psd1', 'ps1xml', 'psc1', 'psrc', 'reg', 'inf', 'url', 'lnk', 'inf', 'url', 'lnk']}
models = {'models': ['3ds', '3mf', 'blend', 'fbx', 'gltf', 'obj', 'stl', 'dae', 'dxf', 'lwo', 'lws', 'lxo', 'ma', 'max', 'mb', 'mesh', 'mesh.xml', 'obj', 'ply', 'skp', 'wrl', 'x', 'x3d', 'x3db', 'x3dv', 'xgl', 'zgl']}
# aggregate all categories into a list
Extensions_categories = [images, audio, video, documents, executables, archives, disc_images, data, internet, programming, system, misc, Linux, Windows, models]

#TODO: Either remove misc or change unknown folder to 'unknown instead of misc
Extensions_Dictionary = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'psd', 'raw', 'heif', 'indd', 'ai', 'eps', 'ps', 'webp'],
    'audio': ['aac', 'aa', 'dvf', 'm4a', 'm4b', 'm4p', 'mp3', 'msv', 'ogg', 'oga', 'raw', 'vox', 'wav', 'wma'],
    'video': ['3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob', 'wmv'],
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




















#TODO unbork this
Target_Directory = './Files/Downloads'

# absolute paths of target files for run-anywhere functionality
def get_absolute_file_paths(folder):

    files = []
    for f in os.listdir(folder):
        # if f is a file
        if os.path.isfile(os.path.join(folder, f)):
            files.append(os.path.abspath(os.path.join(folder, f)))
    return files  

# list of files to ignore
def get_ignore_list():
    #TODO make it possible to add more files to ignore list
    #TODO switch to Extensions_Dictionary from Extensions_categories
    
    ignore_list = []
    for e in Extensions_categories:
        for key, val in e.items():
            ignore_list.append(f'{Target_Directory}/{key}.zip')
    return ignore_list

# All files in Target_Directory, unsorted, with some files ignored
Raw_File_List = [f for f in get_absolute_file_paths(Target_Directory) if f not in get_ignore_list()]

def get_app_made_zips():
    zips = []
    filenames = Extensions_categories.keys()
    for f in filenames:
        print(f)




#get args
parser = argparse.ArgumentParser(description='Takes in arguments from the command line')
# add arguments
parser.add_argument('-a', '--archive', action='store_true', help='Archives files in compressed folders.')
parser.add_argument('-d', '--deduplicate', action='store_true', help='Remove duplicate files when moving files.')
parser.add_argument('-s', '--secure', action='store_true', help='Run security checks on files, quarantines suspicious files')
parser.add_argument('-m', '--move', action='store_true', help='Moves files to their respective folders based on their file extension.')
parser.add_argument('--dry-run', action='store_true', help='Simulate running the program without actually moving files')
#parser.add_argument('-h', action='store_true', help='Displays help message')

_security_checks = parser.parse_args().secure
_remove_duplicates = parser.parse_args().deduplicate
_archive_files = parser.parse_args().archive
_move_files = parser.parse_args().move
_dry_run_only = parser.parse_args().dry_run
#show_help_message = parser.parse_args().help








#get a dictionary of files with extension as key and list of files as value
def create_file_dictionary(file_list):
    """
    Creates a dictionary of files based on their file extension category.

    Args:
        file_list (list): A list of file paths.
        extensions_category_list (list): A list of dictionaries where each dictionary contains a file extension category as the key and a list of file extensions as the value.

    Returns:
        dict: A dictionary where each key is a file extension category and the value is a list of file paths that belong to that category. Files with unknown file extensions are categorized as 'misc'.
    """
    
    #TODO use Extensions_Dictionary instead of Extensions_categories

    file_dictionary = {}
    check_list = []
    for file in file_list:
        for dict in Extensions_categories:
            for key, val in dict.items():
                for ext in val:
                    if file.endswith(f'.{ext}'):
                        if key in file_dictionary:
                            file_dictionary[key].append(file)
                        else:
                            file_dictionary[key] = [file]
                        if file not in check_list:
                            check_list.append(file)
    #handle unknown file types as misc
    for file in file_list:
        if file not in check_list:
            if 'misc' not in file_dictionary:
                file_dictionary['misc'] = [file]
            else:
                file_dictionary['misc'].append(file)
    return file_dictionary

def create_file_dictionary2(file_list):
    """
    Creates a dictionary of files based on their file extension category.

    Args:
        file_list (list): A list of file paths.
        extensions_category_list (list): A list of dictionaries where each dictionary contains a file extension category as the key and a list of file extensions as the value.

    Returns:
        dict: A dictionary where each key is a file extension category and the value is a list of file paths that belong to that category. Files with unknown file extensions are categorized as 'misc'.
    """
    
    #TODO use Extensions_Dictionary instead of Extensions_categories

    file_dictionary = {}
    check_list = []
    for file in file_list:
        for key, val in Extensions_Dictionary.items():
            for ext in val:
                if file.endswith(f'.{ext}'):
                    if key in file_dictionary:
                        file_dictionary[key].append(file)
                    else:
                        file_dictionary[key] = [file]
                    if file not in check_list:
                        check_list.append(file)
    #handle unknown file types as misc
    for file in file_list:
        if file not in check_list:
            if 'misc' not in file_dictionary:
                file_dictionary['misc'] = [file]
            else:
                file_dictionary['misc'].append(file)
    return file_dictionary











def run_security_checks(files_list):
    """
        Check each file for it's MIME type
        if the MIME type does not match the file extension, quarantine the file
        if the file has no extension, quarantine the file
    """
    
    print('running security checks...')
    #check for files with no extension
    for file in files_list:
        if '.' not in file:
            print(f'WARNING: {file} has no extension')
            #quarantine file
            if not os.path.exists(f'{Target_Directory}/quarantine'):
                os.mkdir(f'{Target_Directory}/quarantine')
            shutil.move(file, 'quarantine')
            print(f'File has been moved to {Target_Directory}/quarantine.')
    
    #ask user if they want to delete quarantined files
    response = input('Would you like to delete quarantined files? (y/n): ')
    count = 1
    while response.lower() not in ['y', 'n', 'yes', 'no']:
        if count >= 3:
            response = 'n'
            break
        print('Invalid response, please try again.')
        response = input('Would you like to delete quarantined files? (y/n): ')
        count += 1

    if response.lower() == 'y' or 'yes':
        # delete quarantined files
        os.remove(f'{Target_Directory}/quarantine')
        print('Quarantined files have been deleted.')
    else:
        print('Quarantined files have not been deleted.')
    
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
#find and return duplicate files using regex
import re

def get_duplicate_files(file_list):
    """
    Finds and returns a list of duplicate files in the given file list.

    Args:
        file_list (list): A list of file paths to search for duplicates.

    Returns:
        list: A list of file paths that are duplicates.

    """
    # List of patterns to match
    patterns = [
        re.compile(r'.*\(copy\)\.\w+$'),
        re.compile(r'.*\(\d+\)\.\w+$'),
        re.compile(r'.*\(([02-9]|)1st copy\)\.\w+$'),
        re.compile(r'.*\(([02-9]|)2nd copy\)\.\w+$'),
        re.compile(r'.*\(([02-9]|)3rd copy\)\.\w+$'),
        re.compile(r'.*\(\d*([04-9]|[1][1-3])th copy\)\.\w+$'),
        re.compile(r'.* -Copy\.\w+$'),
        re.compile(r'.* -Copy\(\d+\)\.\w+$'),
    ]

    duplicate_files = []

    for filename in file_list:
        # Check each pattern
        for pattern in patterns:
            match = pattern.match(filename)
            if match:
                duplicate_files.append(filename)
                break
    print(f'{len(duplicate_files)} duplicate files found...')
    return duplicate_files

#safely remove duplicate files. includes dry run functionality
def remove_duplicates_files(files_list):    
    #TODO Test real run
    #get list of duplicate files
    duplicates = get_duplicate_files(files_list)
    #check if dry run
    if _dry_run_only:
        #print status
        print("DRY RUN ONLY, NO FILES WILL BE REMOVED.")
        print ("The following duplicate files would be removed:")
        for d in duplicates:
            #print what would be removed, only filename 
            print(f"\t{d.split('/')[-1]}")
        #stop function
        print("Dry run complete, no files removed.")
        return
    else:
         #print status
        print (f"Removing {len(duplicates)} duplicate files...")
        for file in duplicates:
            #safely remove duplicates
            if os.path.isfile(file):
                #print file being removed
                print(f'\tRemoving {file.split("/")[-1]}...')
                os.remove(file)







#create folders for each key in file_dict
def create_folders(file_dict):
    print('creating folders...')
    for key in file_dict.keys():
        # check if folder exists
        if not os.path.exists(f'{Target_Directory}/{key}'):
            # if not, create folder
            print(f'\t{key}...')
            os.mkdir(f'{Target_Directory}/{key}')

#create archives for each key in file_dict
import zipfile

def create_archives(file_dict):
    #TODO TEST!!! untested
    for key in file_dict.keys():
        # check if archive exists
        if not os.path.exists(f'{Target_Directory}/{key}.zip'):
            # if not, create archive
            shutil.make_archive(f'{Target_Directory}/{key}', 'zip', f'{Target_Directory}/{key}')

# move files into folders, takes file_dict(category:filepath) as an argument
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

#move files into archives, takes file_dict(category:filepath) as an argument
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







#troubleshooting functions
def get_value_count_from_dictionary(d):
    return sum(len(value) for value in d.values())
def get_values_from_dict(d):
    values = []
    for key, value in d.items():
        for v in value:
            values.append(v)
    return values
def find_dif_between_lists(list1, list2):
    differences = []
    for item in list1:
        if item not in list2:
            differences.append(item)
    for item in list2:
        if item not in list1 and item not in differences:
            differences.append(item)
    return differences
def has_shared_value(dict_list):
    values = [v for d in dict_list for v in d.values()]
    return len(values) != len(set(map(str, values)))
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


# main
if __name__ == '__main__':
   
    print('Starting...\n\n')
   
    #print which options are enabled
    print(f'security checks: {_security_checks}')
    print(f'remove duplicates: {_remove_duplicates}')
    print(f'archive files: {_archive_files}')
    print(f'move files: {_move_files}')
    print(f'dry run only: {_dry_run_only}')
    print("\n\n.....................................................\n\n")
    
    # prevent conflict between move and archive
    if _move_files and _archive_files:
        print('ERROR: Cannot move and archive files at the same time.')
        exit()
    

    # run security checks
    if _security_checks:
        run_security_checks(Raw_File_List)
    # run duplicates removal
    if _remove_duplicates:
        remove_duplicates_files(Raw_File_List)
    

    if _move_files or _archive_files:
    # create dictionary of files
        File_Dict = create_file_dictionary2(Raw_File_List)

        # archive or move files
        if _move_files:
            #print(f'moving {get_value_count_from_dict(File_Dict)} files...')
            move_files(File_Dict)
        else:
            #print(f'archiving {get_value_count_from_dictionary(File_Dict)} files...')
            archive_files(File_Dict)
    

    print('Done!')