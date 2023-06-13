import argparse
import os
import zipfile
import shutil
import re
import yaml
import logging

class DataFetcher:
    """
        This class fetches data for other classes. It has the following methods:
        
        - _load_yaml(file): loads a yaml file and returns its contents
        - _set_target_directory(target_directory): sets the target directory. If a target directory is provided as an argument and it exists,
            it will be used as the new target directory. Otherwise, the default target directory from the settings file will be used.
        - _get_absolute_file_paths(folder): returns a list of absolute file paths in the given folder
        - get_app_made_zips(): returns a list of archive names from the extensions dictionary
        - get_file_list(target_directory): returns a list of all files in the target directory
        - get_duplicate_files(file_list): finds and returns a list of duplicate files in the given file list
        
        Parameters:
            fileIOreporter   (object) - an object that handles logging and reporting
            settings_file    (str) - the settings file to get the default target directory from
            extensions_file  (str) - the extensions file to get the extensions dictionary from
            target_directory (str) - the target directory to overwrite the default target directory
                if None, the default target directory will be used
        """
    def __init__(self, fileIOreporter, settings_file, path_to_extensions_file, target_directory = None ): 
        """
            parameters:
               - fileIOreporter (object) - an object that handles logging and reporting
               - settings_file (str) - the settings file to get the default target directory from
               - extensions_file (str) - the extensions file to get the extensions dictionary from
               - target_directory (str) - the target directory to overwrite the default target directory
        """
        self.new_target_directory = ''
        self.reporter = fileIOreporter
        self.settings = self._load_yaml(settings_file)
        self.extensions_dictionary = self._load_yaml(path_to_extensions_file)    
        self._set_target_directory(target_directory)
        self.file_list = self.get_file_list(self.new_target_directory)
        self.new_file_extensions = []

    def _load_yaml(self, path_to_file):
        """
        Loads a yaml file and returns its contents.
        
        parameters: path_to_file (str) - the path to the yaml file to load  
        
        returns: the contents of the yaml file
        """
        with open(path_to_file, 'r') as f:
            #print(f'{yaml.safe_load(f)}')
            return yaml.safe_load(f)
    
    def _set_target_directory(self, target_directory = None):
        """
        Sets the target directory. If a target directory is provided as an argument and it exists,
        it will be used as the new target directory. Otherwise, the default target directory from the settings file will be used.

        Parameters: target_directory (str): The target directory to set as the new target directory. If None, the default target directory from the settings file will be used.

        Returns: None
        """
        if target_directory is not None and os.path.isdir(target_directory) and os.path.exists(target_directory):
            self.reporter.logger.info("Target directory set to:", target_directory)
            self.new_target_directory = target_directory
        else:
            #load default target directory from settings file
            self.reporter.logger.debug("loading default target directory from settings file...")
            self.new_target_directory = self.settings['target_directory']

    def _get_absolute_file_paths(self,folder):
        """
        This function returns a list of absolute file paths in the given folder.
        
        parameters: folder (str) - the folder to get the absolute file paths from
        
        returns: a list of absolute file paths in the given folder
        """
        files = []
        for file in os.listdir(folder):
            # if f is a file
            if os.path.isfile(os.path.join(folder, file)):
                files.append(os.path.abspath(os.path.join(folder, file)))
        return files  
    
    def get_app_made_zips(self):
        """
        This function returns a list of archive names from the extensions dictionary.
        this is used to prevent the app from moving/zipping its own zip files.
        
        parameters: none
        
        returns: a list of archive names from the extensions dictionary
        """
        #TODO add debug logging to this function
        zips = []
        filenames = list(self.extensions_dictionary.keys())
        for file in filenames:
            zips.append(file + '.zip')
        return zips
    
    def get_file_list(self, target_directory = None):
        """
        This function returns a list of all files in the target directory.

        parameters: target_directory (str) - the target directory to get the file list from
        
        returns: a list of absolute file paths in the given folder
        """
        # Get a list of all files in the target directory.
        if target_directory is None:
            print("No target directory set.")
            return None
        return [f for f in self._get_absolute_file_paths(target_directory) if f not in self.get_app_made_zips()]
    
    def get_duplicate_files(self, file_list):
        """
        Finds and returns a list of duplicate files in the given file list using regex patterns.

        parameters: file_list (list) - a list of file paths to search for duplicates

        Returns: list: A list of file paths that match duplicate regex patterns.

        """
        
        #TODO check if original file exists(i.e. file(1).txt and file.txt))
        #TODO if file matches pattern, but no original exists, rename th file to remove the pattern

        
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
                    # if there is a match, and the original file exists, add it to the return list

                    self.reporter.logger.debug(f'duplicate: {filename} \n original: {re.sub(pattern, "", filename)} FOUND')

                    duplicate_files.append(filename)
                    break
                elif match:
                    # if there is a match, but no original file exists, rename the file to remove the pattern

                    self.reporter.logger.debug(f'No original file found for {filename}. Renaming file to remove pattern.')

                    #TODO Test this
                    new_filename = re.sub(pattern, '', filename)
                    os.rename(filename, new_filename)
        return duplicate_files

    def create_file_dictionary(self, file_list):
        """
        Creates a dictionary of files where each key is a file category and the value is a list of the files that belong to that category.
        Saves a list of previously unknown file extensions to self.new_file_extensions. Currently unused. TODO use this to update the extensions dictionary.

            parameters: file_list (list): A list of file paths.
            extensions_category_list (list): A dictionary where each key is a file category and the value is a list of file extensions that belong to that category.

        Returns:
            dict: A dictionary where each key is a file category and the value is a list of file paths that belong to that category. Files with unknown file extensions are categorized as 'unknown'.
        """
        
        #TODO add contingency for files with no extensions
        
        self.reporter.logger.debug("Creating file dictionary...")

        file_dictionary = {}
        check_list = []
        for file in self.file_list:
            #if file has no extension
            if '.' not in file:
                #do something?
                pass
            for key, val in self.extensions_dictionary.items():
                for ext in val:
                    if file.lower().endswith(f'.{ext}'):
                        if key in file_dictionary:
                            file_dictionary[key].append(file)
                        else:
                            file_dictionary[key] = [file]
                        if file not in check_list:
                            check_list.append(file)
        
        #Unknowns go in the unknowns category
        # create list of unknown types for future use
        unknown_types = []
        for file in file_list:
            if file not in check_list:
                if 'unknowns' not in file_dictionary:
                    file_dictionary['unknowns'] = [file]
                else:
                    file_dictionary['unknowns'].append(file)
                ext = file.split('.')[-1]
                unknown_types.append(ext)
                #save list of unknown types for future use
                self.new_file_extensions = unknown_types
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
    """
    
    def __init__(self, fileIOreporter, data_fetcher, archive = False, move = False, remove_duplicates = False):
        
        self.fetcher = data_fetcher
        self.target_directory = self.fetcher.new_target_directory
        self.extensions_dictionary = self.fetcher.extensions_dictionary
        self.file_list = self.fetcher.file_list
        #...CLI arguments...
        self._archive_files = archive
        self._move_files = move
        self._remove_duplicates = remove_duplicates
        self.reporter = fileIOreporter

    #create folders for each key in file_dict
    def create_folders(self, file_dict):
        #if self._verbose_output:
            #TODO replace with logger
         #   print('creating folders...')
        folders_created = []
        for key in file_dict.keys():
            # check if folder exists
            if not os.path.exists(f'{self.target_directory}/{key}'):
                # if not, create folder
                #if self._verbose_output:
                    #print(f'\t{key}...')
                os.mkdir(f'{self.target_directory}/{key}')
                folders_created.append(key)
        #if self._verbose_output:
         #   for f in folders_created:
          #      print(f'\t{f} folder created.')

    #create archives for each key in file_dict
    def create_archives(self, file_dict):
        for key in file_dict.keys():
            # check if archive exists
            if not os.path.exists(f'{self.target_directory}/{key}.zip'):
                # if not, create archive
                shutil.make_archive(f'{self.target_directory}/{key}', 'zip', f'{self.target_directory}/{key}')
   
    #safely remove duplicate files
    def remove_duplicates_files(this):    
        #TODO move files to temp folder and delete later
        #TODO add permanant delete option to settings.yaml
        #TODO add restore option
        #TODO rename duplicate with no original
        #get list of duplicate files
        duplicates = this.fetcher.get_duplicate_files(this.fetcher.file_list)
        files_remove = 0
        if len(duplicates) == 0:
            #TODO replace with logging
            print('No duplicate files found.')
            return
        else:
            #print status
            #TODO replace with logging
            print (f"Removing {len(duplicates)} duplicate files...")
            for file in duplicates:
                #safely remove duplicates
                if os.path.isfile(file):
                    #print file being removed
                    print(f'\tRemoving {file.split("/")[-1]}...')
                    os.remove(file)
                    files_remove += 1
        #TODO replace with logging
        print(f'{files_remove} files removed.')
    
    def move_files(self, file_dict):
        all_files_moved = True
        self.create_folders(file_dict)
        file_count = sum(len(value) for value in file_dict.values())
        #TODO replace with logging
        print(f'Moving {file_count} files...')
        action_count = 0
        for file_category, file_list in file_dict.items():
            #TODO replace with logging
            print(f'Moving {len(file_list)} file(s) to {file_category}...')
            for file in file_list:
                if os.path.exists(f'{file}'):

                    #TODO add error handling
                    #TODO replace with logging
                    print(f'\tMoving {file}...')
                    #strip filepath from filename
                    file_no_path = file.split('/')[-1]
                    # check if file is already present in target directory
                    if os.path.exists(f'{self.target_directory}/{file_category}/{file_no_path}'):
                        #TODO add setting to overwrite existing files or skip
                        #TODO replace with logging
                        print(f'\t{file_no_path} already exists, in {file_category}. Skipping...')
                        continue
                    else:
                        shutil.move(f'{file}', f'{self.target_directory}/{file_category}/{file_no_path}')
                        action_count += 1
                else:
                    #TODO replace with logging
                    print(f'\t{file} does not exist, skipping...')
                    all_files_moved = False
        #TODO replace with logging
        print(f'{action_count} files moved.')
        return all_files_moved

    def archive_files(self, file_dict):
        all_files_archived = True
        self.create_archives(file_dict)
        file_count = sum(len(value) for value in file_dict.values())
        #TODO replace with logging
        print(f'Archiving {file_count} files...')
        action_count = 0    
        for file_category, file_list in file_dict.items():
            #TODO replace with logging
            print(f'Archiving {len(file_list)} file(s) to {file_category}.zip...')
            for file in file_list:
                if os.path.exists(f'{file}'):

                    #TODO add error handling
                    #TODO replace with logging
                    print(f'\tArchiving {file}...')
                    # check if file is already present in archive
                    with zipfile.ZipFile(f'{self.target_directory}/{file_category}.zip', 'a') as zip:
                        if file in zip.namelist():
                            #TODO add setting to overwrite existing files or skip
                            #TODO replace with logging
                            print(f'\t{file} already exists in {file_category}.zip. Skipping...')
                            zip.close()
                            continue
                        else:
                            #remove absolute path from filename before zipping
                            zip.write(f'{file}', arcname=f'{file.split("/")[-1]}')
                            #remove original file
                            os.remove(f'{file}')
                            action_count += 1
                            zip.close()
                else:
                    #TODO replace with logging
                    print(f'\t{file} does not exist, skipping...')
                    all_files_archived = False
        #TODO replace with logging
        print(f'{action_count} files archived.')
        return all_files_archived

    def organize_files(self):
        """
        this function will call the other functions in this class to organize the files
        return bool to indicate total success or partial to total failure
        """
       
        duplicates_removed_success = True
        files_archived_success = True
        files_moved_sucess = True
        if self._remove_duplicates:
            duplicates_removed_success = self.remove_duplicates_files()
        if self._archive_files:
            files_archived_success = self.archive_files(self.fetcher.create_file_dictionary(self.fetcher.get_file_list(self.fetcher.new_target_directory)))
        elif self._move_files:
            files_moved_sucess = self.move_files(self.fetcher.create_file_dictionary(self.fetcher.get_file_list(self.fetcher.new_target_directory)))
        
        return {"duplicate_files_removed": duplicates_removed_success,
                "files_archived": files_archived_success,
                "files_moved_success": files_moved_sucess,
                "all": duplicates_removed_success and files_archived_success and files_moved_sucess}


class SecurityManager:
    """
        This class will handle security functions such as:
            - checking if the user has permission to access the target directory
            - checking if the user has permission to access the extensions file
            - checking if the user has permission to access the settings file
            - running security checks on files before other operations
    """
    
    def __init__(self, target_directory):
        self.target_directory = target_directory
        
    def check_write_permissions(self, target_directory):
        """takes directory path as argument
           returns bool and string"""

        if not os.access(target_directory, os.W_OK):
             return False, "User does not have write permissions to target directory"
        else:
            return True, "User has write permissions to target directory"


class FileIOReporter:
    """
    this class will handle all logging and dry run functions


    logging rules:
        - always log (info)):
            - start of program
            - start of each function
            - end of each signficant function
            - end of program
        - log if verbose (debug):
            - each step of each function
            - each file moved
            - each file archived
            - each file removed/moved to duplicates folder
            - each file quarantined
            - each file skipped
        - log if warning:
            - category folder not found
            - category archive not found
            - file already exists
        - log if error:
            -
            - file not found
        - log if critical:
            - settings file not found
            - extensions file not found
            - target directory not found
            - target directory not writable
            - permissions error

    """
   
    def __init__(self, target_directory, move_mode, archive_mode, remove_duplicates_mode, log_level=logging.DEBUG, data_fetcher=None):
        self._dry_move = move_mode
        self._dry_archive = archive_mode
        self._dry_remove_duplicates = remove_duplicates_mode        
        
        self.logger = logging.getLogger("system_logger")

        self.logger.setLevel(log_level)

        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        self.fetcher = data_fetcher

    def dry_move(self):
        self.logger.info('Dry run: Moving files...')
        pass

    def dry_archive(self):
        self.logger.info('Dry run: Archiving files...')
        pass

    def dry_remove_duplicates(self):
        self.logger.info('Dry run: Removing duplicates...')
        pass

    def dry_run(self):
        if self.dry_remove_duplicates:
            self.dry_remove_duplicates()
        if self.dry_archive:
            self.dry_archive()
        elif self.dry_move:
            self.dry_move()
        pass
    

class Main:
    """
    gets arguments from command line
    creates instances of FileIOReporter, DataFetcher and FileOrganizer
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
        parser.add_argument('-t', '--target', type=str, help=f'Target directory to organize. Default is /home/user/Downloads')
        self.args = parser.parse_args()

    def run(self):

        reporter = FileIOReporter(self.args.target, 
                                  move_mode=self.args.move, 
                                  archive_mode=self.args.archive, 
                                  remove_duplicates_mode=self.args.rm_duplicates, 
                                  log_level = logging.DEBUG if self.args.verbose else logging.INFO)

        fetcher = DataFetcher( fileIOreporter = reporter, 
                               settings_file = './Settings.yaml', 
                               path_to_extensions_file = './Extensions.yaml', 
                               target_directory = self.args.target)

        reporter.fetcher = fetcher

        reporter.logger.info("Starting...")

        organizer = FileOrganizer( fileIOreporter = reporter,
                                   data_fetcher= fetcher,
                                   archive = self.args.archive,
                                   move = self.args.move,
                                   remove_duplicates = self.args.rm_duplicates)
        
        organizer_sucess = True

        if self.args.dry_run:
            reporter.dry_run()
        elif self.args.archive and self.args.move:
            reporter.logger.error("Cannot archive and move at the same time. Please choose one or the other.")
            organizer_sucess = False
        else:
            organizer_sucess = organizer.organize_files()["all"]

        if organizer_sucess:
            reporter.logger.info("Finished.")
        else:
            reporter.logger.error("Finished with errors.")

# main
if __name__ == '__main__':

    main = Main()
    main.run()