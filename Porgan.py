import argparse
import os
import zipfile
import shutil
import re
import yaml

#TODO add more file extensionss
Extensions_Dictionary = {
   """  'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'psd', 'raw', 'heif', 'indd', 'ai', 'eps', 'ps', 'webp'],
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
    'models': ['3ds', '3mf', 'blend', 'fbx', 'gltf', 'obj', 'stl', 'dae', 'dxf', 'lwo', 'lws', 'lxo', 'ma', 'max', 'mb', 'mesh', 'mesh.xml', 'obj', 'ply', 'skp', 'wrl', 'x', 'x3d', 'x3db', 'x3dv', 'xgl', 'zgl'] """
}

with open('Extensions.yaml', 'r') as f:
        Extensions_Dictionary = yaml.safe_load(f)


#set to folder to be organized
Target_Directory = './Files/Downloads'

#absolute paths of target files for run-anywhere functionality
def get_absolute_file_paths(folder):

    files = []
    for f in os.listdir(folder):
        # if f is a file
        if os.path.isfile(os.path.join(folder, f)):
            files.append(os.path.abspath(os.path.join(folder, f)))
    return files  

#get all possible zip files that can be made
def get_app_made_zips():
    zips = []
    filenames = list(Extensions_Dictionary.keys())
    for f in filenames:
        zips.append(f + '.zip')
    return zips

#get all files that are not created by this app
def get_files_in_target_directory():
    return [f for f in get_absolute_file_paths(Target_Directory) if f not in get_app_made_zips()]

#get args
parser = argparse.ArgumentParser(description='Organizes files by removing duplicates, archiving, or moving them to their respective folders based on their file extension.')
# add arguments
parser.add_argument('-a', '--archive', action='store_true', help='Archives files to their respective zip files based on their file extension.')
parser.add_argument('-m', '--move', action='store_true', help='Moves files to their respective folders based on their file extension.')
parser.add_argument('-d', '--rm-duplicates', action='store_true', help='Remove duplicate files.')
parser.add_argument('-s', '--secure', action='store_true', help='Run security checks on files, quarantines suspicious files')
parser.add_argument('--dry-run', action='store_true', help='Simulate running the program without actually moving/removing files')
parser.add_argument('-v', '--verbose', action='store_true', help='Displays verbose output')
parser.add_argument('-t', '--target', type=str, help=f'Target directory to organize. Defaults to {Target_Directory}')

# parse arguments
_archive_files = parser.parse_args().archive
_move_files = parser.parse_args().move
_remove_duplicates = parser.parse_args().rm_duplicates
_security_checks = parser.parse_args().secure
_dry_run_only = parser.parse_args().dry_run
_verbose_output = parser.parse_args().verbose

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
    
    #TODO add contingency for files with no extensions

    file_dictionary = {}
    check_list = []
    for file in file_list:
        for key, val in Extensions_Dictionary.items():
            for ext in val:
                if file.lower().endswith(f'.{ext}'):
                #if file.endswith(f'.{ext}'):
                    if key in file_dictionary:
                        file_dictionary[key].append(file)
                    else:
                        file_dictionary[key] = [file]
                    if file not in check_list:
                        check_list.append(file)
    #handle unknown file types as unknown
    for file in file_list:
        if file not in check_list:
            if 'unknowns' not in file_dictionary:
                file_dictionary['unknowns'] = [file]
            else:
                file_dictionary['unknowns'].append(file)
    return file_dictionary

#quarantine suspicious files
def run_security_checks(files_list):
    """
        Check each file for it's MIME type
        if the MIME type does not match the file extension, quarantine the file
        if the file has no extension, quarantine the file
    """
    print('Not ready for testing....')
    return
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
        shutil.rmtree(f'{Target_Directory}/quarantine')
        print('Quarantined files have been deleted.')
    else:
        print('Quarantined files have not been deleted.')

#find and return duplicate files using regex
def get_duplicate_files(file_list):
    """
    Finds and returns a list of duplicate files in the given file list.

    Args:
        file_list (list): A list of file paths to search for duplicates.

    Returns:
        list: A list of file paths that are duplicates.

    """
    #TODO check if original file exists(i.e. file(1).txt and file.txt))
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
    #print(f'{len(duplicate_files)} duplicate files found...')
    return duplicate_files

#safely remove duplicate files. includes dry run functionality
def remove_duplicates_files(files_list):    
    #get list of duplicate files
    duplicates = get_duplicate_files(files_list)
    if len(duplicates) == 0:
        print('No duplicate files found.')
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
    if _verbose_output:
        print('creating folders...')
    folders_created = []
    for key in file_dict.keys():
        # check if folder exists
        if not os.path.exists(f'{Target_Directory}/{key}'):
            # if not, create folder
            if _verbose_output:
                print(f'\t{key}...')
            os.mkdir(f'{Target_Directory}/{key}')
            folders_created.append(key)
    if _verbose_output:
        for f in folders_created:
            print(f'\t{f} folder created.')

#create archives for each key in file_dict
def create_archives(file_dict):
    for key in file_dict.keys():
        # check if archive exists
        if not os.path.exists(f'{Target_Directory}/{key}.zip'):
            # if not, create archive
            shutil.make_archive(f'{Target_Directory}/{key}', 'zip', f'{Target_Directory}/{key}')

#move or archive files, takes file_dict(category:filepath) as an argument
def move_or_archive_files(file_dict):
    #default mode is move
    #TODO check if file already exists in target folder/archive
    #set action for status message
    action = ['Moving','moved']
    to_zip = ''

    if _archive_files:
        action = ['Archiving','archived']
        to_zip = '.zip'
        create_archives(file_dict)
    else:
        create_folders(file_dict)
    #print status, ex: Moving 5 files..., Archiving 5 files...
    print(f'{action[0]} {get_value_count_from_dictionary(file_dict)} files...')
    
    # iterate through file_dict
    action_count = 0
    for file_category, file_list in file_dict.items():
        # iterate through files in value
        print(f'{action[0]} {len(file_list)} file(s) to {file_category}{to_zip}...')
        for file in file_list:
            # check if file exists
            if os.path.exists(f'{file}'):
                # if so, move file to folder
                print(f'\t{action[0]} {file}...')
                
                #archiving files
                if _archive_files:
                    if os.path.exists(f'{Target_Directory}/{file_category}.zip'):
                        with zipfile.ZipFile(f'{Target_Directory}/{file_category}.zip', 'a') as zip:
                            #remove absolutepath from filename before zipping
                            zip.write(f'{file}', arcname=f'{file.split("/")[-1]}')
                            #remove original file
                            os.remove(f'{file}')
                            action_count += 1
                    else:
                        #print error message
                        print(f'\t{Target_Directory}/{file_category}.zip does not exist, skipping...')
                
                #Moving files
                else:
                    if os.path.exists(f'{Target_Directory}/{file_category}'):
                        #move file
                        #strip filepath from filename
                        file_no_path = file.split('/')[-1]
                        shutil.move(f'{file}', f'{Target_Directory}/{file_category}/{file_no_path}')
                        action_count += 1
                    else:
                    #print error message
                        print(f'\t{Target_Directory}/{file_category} does not exist, skipping...')
    #print status
    # ex: 5 files moved., 5 files archived.
    print(f'{action_count} files {action[1]}.')

#dry run. prints what would happen without actually changing anything
def dry_run_mode(file_dict, file_list):

    if _security_checks:
        print('Dry run mode: limited security check only.')
    if _remove_duplicates:
        #get list of duplicate files
        duplicates = get_duplicate_files(file_list)
        #check if duplicates exist
        if len(duplicates) == 0:
            print('No duplicate files found.')
            return
        #if duplicates exist
        else:
            print("Dry run mode: No files will be removed.")
            print ("The following duplicate files would be removed:")
            for d in duplicates:
            #print what would be removed, only filename 
                print(f"\t{d.split('/')[-1]}")
            print("Dry run complete, no files removed.")    
    if _move_files or _archive_files:
        action = ['Moving','moved']
        to_zip = ''
        if _archive_files:
            action = ['Archiving','archived']
            to_zip = '.zip'
        
        print(f'Dry run mode: no files will be {action[1]}.')
        #print which folders/archives will be created
        #and which files go in which folders/archives
        for key, value in file_dict.items():
            #ex: Moving 5 files to Documents., Archiving 5 files to Documents.zip.
            print(f'{action[0]} {len(value)} file(s) to {key}{to_zip}...')
            for file in value:
                print(f'\t{file.split("/")[-1]}...')
        print(f'Dry run complete, no files {action[1]}.')
    
#debug info
def print_debug_info():
    """
    Prints the current status of the enabled options for the PORGAN program.
    """
    statements = [("security_checks", _security_checks), 
                  ("remove_duplicates", _remove_duplicates), 
                  ("archive_files", _archive_files), 
                  ("move_files", _move_files), 
                  ("dry_run_only", _dry_run_only), 
                  ("verbose", _verbose_output)]
    print('\n')
    # Print the statements as two columns
    for statement in statements:
        print("{:<20} {}".format(statement[0], statement[1]))
    print('\n')
    
#troubleshooting/debugging functions
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
    print('Starting...')
    
    if len(get_files_in_target_directory()) == 0:
        print('No files found, exiting...')
        exit()

    #debug output
    if _verbose_output:
      print_debug_info()
    print(".....................................................\n\n")
    
    if _dry_run_only:
        dry_run_mode(create_file_dictionary(get_files_in_target_directory()), get_files_in_target_directory())
        print("Done!")
        exit()

    # Preliminary tasks.................

    # run security checks
    if _security_checks:
        run_security_checks(get_files_in_target_directory())
    # run duplicates removal
    if _remove_duplicates:
        remove_duplicates_files(get_files_in_target_directory())
    
    #Primary tasks......................

    if _move_files ^ _archive_files:
    # Either _move_files or _archive_files is True, but not both
       move_or_archive_files(create_file_dictionary(get_files_in_target_directory()))
    elif _move_files and _archive_files:
    # Both _move_files and _archive_files are either True or False
        print('ERROR: Cannot move and archive files at the same time.')
        print('exiting...')
        exit()
    
    print('Done!')