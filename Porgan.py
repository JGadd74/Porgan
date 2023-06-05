import argparse
import os
import zipfile
import shutil
import re
import yaml


# in OO version of Porgan, these are the classes that will be used
# the data_fetcher class will be used to get the data from settings and extensions files
    # settings includes the default target directory
    # extensions includes the file extensions and their corresponding categories (extensions dictionary)
#the Organizer class will be used to organize the files
#the main function will be used to run the program
    # the main function will take arguments from the command line
    # the main function will create an instance of the data_fetcher class
    # the main function will create an instance of the Organizer class
    # the main function will call the organize_files method of the Organizer class


class DataFetcher:
    # this fetches data for other classes
    """
    get files list
    get extensions dictionary from yaml
    get settings from yaml (target directory)
    get duplicate files from files list
    get archive names from extensions dictionary

    parameters:
        settings_file    (str) - the settings file to get the default target directory from
        extensions_file  (str) - the extensions file to get the extensions dictionary from
        target_directory (str) - the target directory to overwrite the default target directory
            if None, the default target directory will be used
    """
    new_target_directory = ''

    def __init__(self, settings_file, extensions_file, target_directory = None ):
        self.settings = self._load_yaml(settings_file)
        self.extensions_dictionary = self._load_yaml(extensions_file)    
        self._set_target_directory(target_directory)
        self.file_list = self.get_file_list(self.new_target_directory)

    def _load_yaml(self, file):
        with open(file, 'r') as f:
            #print(f'{yaml.safe_load(f)}')
            return yaml.safe_load(f)
    
    def _set_target_directory(self, target_directory = None):
        """
        Sets the target directory. If a target directory is provided as an argument and it exists,
        it will be used as the new target directory. Otherwise, the default target directory from the settings file will be used.

        Parameters:
            target_directory (str): The target directory to set as the new target directory. If None, the default target directory
                                    from the settings file will be used.

        Returns:
            None
        """
        if target_directory is not None and os.path.isdir(target_directory) and os.path.exists(target_directory):
            print("Target directory set to:", target_directory)
            self.new_target_directory = target_directory
        else:
            #load default target directory from settings file
            #print("Settings:", self.settings)
            print("loading default target directory from settings file...")
            self.new_target_directory = self.settings['target_directory']
            #print("Target directory:", self.new_target_directory)

    def _get_absolute_file_paths(self,folder):
        files = []
        for f in os.listdir(folder):
            # if f is a file
            if os.path.isfile(os.path.join(folder, f)):
                files.append(os.path.abspath(os.path.join(folder, f)))
        return files  
    
    def get_app_made_zips(self):
        zips = []
        filenames = list(Extensions_Dictionary.keys())
        for f in filenames:
            zips.append(f + '.zip')
        return zips
    
    def get_file_list(self, target_directory = None):
        # Get a list of all files in the target directory.
        if target_directory is None:
            print("No target directory set.")
            return None
        return [f for f in self._get_absolute_file_paths(target_directory) if f not in get_app_made_zips()]
    
    def get_duplicate_files(self, file_list):
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
                # If there is a match, and the original file exists, add it to the list
                if match and re.sub(pattern, '', filename) in file_list:
                    duplicate_files.append(filename)
                    break
        return duplicate_files
    
    def create_file_dictionary(self, file_list):
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
        for file in self.file_list:
            for key, val in self.extensions_dictionary.items():
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
    
class FileOrganizer:
    """
        uses the data from self.data_fetcher to organize the files
        organize files into file_dictionary (create_file_dictionary)
        create folders
        create archives
        move files
        archive files
        remove duplicate files

        only class that makes changes to the file system

        parameters:
            target_directory      (str): The directory to organize files in.
            archive               (bool): Whether or not to archive files.
            move                  (bool): Whether or not to move files.
            remove_duplicates     (bool): Whether or not to remove duplicate files.
            verbose_output        (bool): Whether or not to print verbose output.
    """
    def __init__(self, target_directory = None, archive = False, move = False, remove_duplicates = False, verbose_output=False):
        
        self.data_fetcher = DataFetcher('./Settings.yaml','./Extensions.yaml', target_directory)
        self.target_directory = self.data_fetcher.new_target_directory
        self.extensions_dictionary = self.data_fetcher.extensions_dictionary
        self.file_list = self.data_fetcher.file_list
        #...CLI arguments...
        self.archive = archive
        self.move = move
        self.remove_duplicates = remove_duplicates
        self._verbose_output = verbose_output

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
   
    #safely remove duplicate files
    def remove_duplicates_files(this, files_list):    
        #get list of duplicate files
        duplicates = this.data_fetcher.get_duplicate_files(this.data_fetcher.file_list)
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
    
    def organize_files(self):
        #placeholder

        # Implement the logic to organize files based on extensions_dictionary.
        """
        if self._remove_duplicates:
        if self._archive
        if self._move
        """
        
        pass

class SecurityManager:
    """
        This class will handle security functions such as:
            - checking if the user has permission to access the target directory
            - checking if the user has permission to access the extensions file
            - checking if the user has permission to access the settings file
            - running security checks on files before other operations
    """
    
    
    def __init__(self):
        pass

class Main:
    """
    gets arguments from command line
    creates instances of FileOrganizer
    has run() method that runs the program
    """
    def __init__(self):
        #get arguments from command line
        parser = argparse.ArgumentParser()
        # Define the arguments...
        parser = argparse.ArgumentParser(description='Organizes files by removing duplicates, archiving, or moving them to their respective folders based on their file extension.')
        # add arguments
        parser.add_argument('-a', '--archive', action='store_true', help='Archives files to their respective zip files based on their file extension.')
        parser.add_argument('-m', '--move', action='store_true', help='Moves files to their respective folders based on their file extension.')
        parser.add_argument('-d', '--rm-duplicates', action='store_true', help='Remove duplicate files.')
        parser.add_argument('-s', '--secure', action='store_true', help='Run security checks on files, quarantines suspicious files')
        parser.add_argument('--dry-run', action='store_true', help='Simulate running the program without actually moving/removing files')
        parser.add_argument('-v', '--verbose', action='store_true', help='Displays verbose output')
        parser.add_argument('-t', '--target', type=str, help=f'Target directory to organize. Defaults to {Target_Directory}')
        self.args = parser.parse_args()

    def run(self):
        print('Starting...')

        organizer = FileOrganizer(target_directory = self.args.target,
                 archive = self.args.archive,
                 move = self.args.move,
                 remove_duplicates = self.args.rm_duplicates,
                 verbose_output=self.args.verbose)
                
        if self.args.dry_run:
            print("Running in dry run mode.")
        else:
            organizer.organize_files()
        print("Done.")

# main
if __name__ == '__main__':

    main = Main()
    main.run()