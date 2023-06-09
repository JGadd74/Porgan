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
        # make file_list getter
        self.file_list = self.get_file_list() 
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
            self.reporter.logger.info("Target directory set to:", target_directory) # type: ignore
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
        zips = []
        filenames = list(self.extensions_dictionary.keys())
        for file in filenames:
            zips.append(file + '.zip')
        return zips
    
    def get_app_made_folders(self):
        """
        This function returns a list of folder names from the extensions dictionary.
        this is used to prevent the app from moving/zipping its own folders.

        parameters: none

        returns: a list of folder names from the extensions dictionary
        """
        folder_names = list(self.extensions_dictionary.keys())
        return folder_names

    def get_file_list(self):
        """
        This function returns a list of all files in the target directory.

        parameters: target_directory (str) - the target directory to get the file list from
        
        returns: a list of absolute file paths in the given folder
        """
        # Get a list of all files in the target directory.
        if self.new_target_directory == '':
            self.reporter.logger.error("No target directory provided. Exiting...")
            exit()
        return [f for f in self._get_absolute_file_paths(self.new_target_directory) if f not in self.get_app_made_zips()]
    
    def strip_duplicate_pattern(self, file, pattern):
        new_filename = re.sub(pattern, "", file)
        new_filename = new_filename.replace(" ", "")
        return new_filename
    
    def get_duplicate_files(self, file_list):
        """
        Finds and returns a list of duplicate files in the given file list using regex patterns.

        parameters: file_list (list) - a list of file paths to search for duplicates

        Returns: tuple(list, list<tuple>) - a list of duplicate files and a list of tuples containing the an orphan and its regex pattern

        """
        
        #TODO compare files in target_dir with files in app made folders/zips
        #TODO if a file has multiple duplicates, print as group

        # List of patterns to match
        patterns = [
            #(copy)
            re.compile(r'\(copy\)(?=\.\w+$)'),
            #(Copy)
            re.compile(r'\(Copy\)(?=\.\w+$)'),
            #(n)
            #re.compile(r'\(\d+\)(?=\.\w+$)'),
            re.compile(r'\(\d+\)'),
            #(nst copy)
            re.compile(r'\((?:[02-9]|[1-9](?<!1)\d*)1st copy\)'),
            #(nnd copy)
            re.compile(r'\((?:[02-9]|[1-9](?<!1)\d*)nd copy\)'),
            #(nrd copy)
            re.compile(r'\((?:[02-9]|[1-9](?<!1[0-3]))\d*rd copy\)'),
            #(nth copy)
            re.compile(r'\((?:\d*[04-9]|[1][1-3])th copy\)'),
        ]

        duplicate_files = []
        matches_with_no_original = []

        for filename in file_list:
            # Check each pattern
            for pattern in patterns:
                #match = pattern.match(filename)
                match = re.search(pattern, filename)
                # If there is a match, and the original file exists, add it to the list
                if match and self.strip_duplicate_pattern(filename, pattern) in file_list:
                    # if there is a match, and the original exists, add duplicate file to the return list

                    duplicate_files.append(filename)
                    filename = os.path.basename(filename)
                    self.reporter.logger.debug(f'duplicate: {filename} \n\t\t\t original:  {self.strip_duplicate_pattern(filename, pattern)}\n')
                    break
                elif match:
                    matches_with_no_original.append((filename, pattern))
                    filename = os.path.basename(filename)
                    self.reporter.logger.debug(f'Orphan duplicate found: {filename}')
        
        return duplicate_files, matches_with_no_original

    def create_file_dictionary(self, file_list):
        """
        Creates a dictionary of files where each key is a file category and the value is a list of the files that belong to that category.
        Saves a list of previously unknown file extensions to self.new_file_extensions. Currently unused. TODO use this to update the extensions dictionary.

            parameters: file_list (list): A list of file paths.
            extensions_category_list (list): A dictionary where each key is a file category and the value is a list of file extensions that belong to that category.

        Returns:
            dict: A dictionary where each key is a file category and the value is a list of file paths that belong to that category. Files with unknown file extensions are categorized as 'unknown'.
        """
        
 
        self.reporter.logger.debug("Creating file dictionary...")

        file_dictionary = {}
        check_list = []
        for file in file_list:
            #if file has no extension
            if '.' not in file:
                #do something?
                # currently gets picked up in the unknowns category
                # later, check mime/media type for identification.
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
    
    def get_target_directory(self):
        return self.new_target_directory


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

        self.reporter.logger.debug('Creating folders...')
        
        folders_created = []
        
        for key in file_dict.keys():
            # check if folder exists
            if not os.path.exists(f'{self.target_directory}/{key}'):
                
                self.reporter.logger.debug(f'\t{key}')
                
                os.mkdir(f'{self.target_directory}/{key}')
                
                folders_created.append(key)

        self.reporter.logger.debug(f'Folders created: {len(folders_created)}')
        
        return folders_created

    #create archives for each key in file_dict
    def create_archives(self, file_dict):
        self.reporter.logger.debug('Creating archives...')

        archives_created = []

        for key in file_dict.keys():
            # check if archive exists
            if not os.path.exists(f'{self.target_directory}/{key}.zip'):
                # if not, create archive
                shutil.make_archive(f'{self.target_directory}/{key}', 'zip', f'{self.target_directory}/{key}')
                
                archives_created.append(f'{key}.zip')
                
                self.reporter.logger.debug(f'\t{key}.zip')
        
        self.reporter.logger.debug(f'Archives created: {len(archives_created)}')
        
        return archives_created
    
    #rename orphaned duplicate files
    def rename_orphaned_duplicates(self, orphaned_duplicates):
        if self.fetcher.settings['rename_orphaned_duplicates'] == True:
            for file, pattern in orphaned_duplicates:
                new_file_name = re.sub(pattern, '', file)
                os.rename(file, new_file_name)
        
    #safely remove/rename duplicate files
    def remove_duplicates_files(self):   
        #TODO test orphan renaming
        #TODO move files to temp folder and delete later
        #TODO add permanant delete option to settings.yaml
        #TODO add restore functionionality
        #TODO add return value for success/failure
        
        all_duplicates_removed = True
        all_orphans_renamed = True

        #get list of duplicate files and orphaned duplicates
        #duplicates, orphans(tuple(file, pattern))
        duplicates, orphaned_duplicates = self.fetcher.get_duplicate_files(self.fetcher.file_list)

        files_removed = 0
        files_renamed = 0
        
        #If there are no duplicates, return
        if len(duplicates) == 0 and len(orphaned_duplicates) == 0:
            self.reporter.logger.info('No duplicate files found.')
            return
        #if there are duplicates
        else:
            #if no settings are enabled, return
            if self.fetcher.settings['rename_orphaned_duplicates'] == False and self.fetcher.settings['delete_duplicate_files'] == False:
                self.reporter.logger.info('No action taken. Please enable rename_orphaned_duplicates or delete_duplicate_files in settings.yaml.')
                all_duplicates_removed = False
                all_orphans_renamed = False
                return
            #rename orphaned duplicates if setting["rename_orphaned_duplicates"] is true and there are orphaned duplicates
            if self.fetcher.settings['rename_orphaned_duplicates'] == True and len(orphaned_duplicates) > 0:
                self.reporter.logger.info(f'Renaming {len(orphaned_duplicates)} orphaned duplicate files...')
                #self.rename_orphaned_duplicates(orphaned_duplicates)
                for file, pattern in orphaned_duplicates:
                    #safely rename orphaned duplicate
                    if os.path.isfile(file):
                        new_filename = self.fetcher.strip_duplicate_pattern(file, pattern)

                        self.reporter.logger.debug(f'\tRenaming {os.path.basename(file)} to {os.path.basename(new_filename)}...')
                        os.rename(file, new_filename)
                        #check if file was renamed
                        if not os.path.exists(new_filename):
                            all_orphans_renamed = False
                            self.reporter.logger.error(f'Failed to rename {os.path.basename(file)} to {os.path.basename(new_filename)}')
                            continue

                        files_renamed += 1

                self.reporter.logger.info(f'{files_renamed} files renamed.')
            
            #if setting['delete_duplicate_files] there are duplicate files to remove
            if self.fetcher.settings['delete_duplicate_files'] and len(duplicates) > 0:
                #print duplicate removal status
                self.reporter.logger.info (f"Removing {len(duplicates)} duplicate files...")

                for file in duplicates:
                    #safely remove duplicate
                    if os.path.isfile(file):
                        #print file being removed
                        self.reporter.logger.debug(f'\tRemoving {os.path.basename(file)}...')
                        os.remove(file)
                        #check if file was removed
                        if os.path.exists(file):
                            all_duplicates_removed = False
                            self.reporter.logger.error(f'Failed to remove {os.path.basename(file)}')
                            continue
                        files_removed += 1
        
                self.reporter.logger.info(f'{files_removed} files removed.\n')
        return all_duplicates_removed and all_orphans_renamed
    
    #move files into folders
    def move_files(self, file_dict):

        all_files_moved = True

        self.create_folders(file_dict)

        file_count = sum(len(value) for value in file_dict.values())
        file_count = len(self.fetcher.get_file_list())

        self.reporter.logger.info(f'Moving {file_count} files...')

        action_count = 0

        for file_category, file_list in file_dict.items():
            self.reporter.logger.debug(f'Moving {len(file_list)} file(s) to {file_category}...')
            for file in file_list:
                #check if file exists
                if os.path.exists(f'{file}'):
                    #TODO add more robust error handling
                    
                    file_no_path = os.path.basename(file)

                    self.reporter.logger.debug(f'\tMoving {file_no_path}...')
                    #strip filepath from filename
                    
                     #TODO replace this with try/except
                    if shutil.move(f'{file}', f'{self.target_directory}/{file_category}/{file_no_path}'):
                        self.reporter.logger.debug(f'\t{file_no_path} moved successfully.')
                    action_count += 1
                else:
                    self.reporter.logger.error(f'\t{file} does not exist, skipping...')
                    all_files_moved = False
        
        self.reporter.logger.info(f'{action_count} files moved.')
        self.reporter.logger.debug(f'All files moved: {all_files_moved}')
        
        return all_files_moved

    #compress files into archives
    def archive_files(self, file_dict):
        #TODO consistent messages
        all_files_archived = True

        self.create_archives(file_dict)

        file_count = sum(len(value) for value in file_dict.values())
        
        self.reporter.logger.info(f'Archiving {file_count} files...')
        
        action_count = 0    
        
        for file_category, file_list in file_dict.items():

            self.reporter.logger.debug(f'Archiving {len(file_list)} file(s) to {file_category}.zip...')
            for file in file_list:
                if os.path.exists(f'{file}'):
                    
                    file_no_path = os.path.basename(file)

                    #TODO add error handling
                    self.reporter.logger.debug(f'\tArchiving {file_no_path}...')
                    # check if file is already present in archive
                    with zipfile.ZipFile(f'{self.target_directory}/{file_category}.zip', 'a') as zip:
                        
                        if file in zip.namelist():
                            #TODO add prompt or setting to overwrite existing files
                            self.reporter.logger.info(f'\t{file_no_path} already exists in {file_category}.zip. Skipping...')
                            continue

                        else:
                            #remove absolute path from filename before zipping
                            zip.write(f'{file}', arcname=file_no_path)
                            
                            #check if file was added to archive
                            if file_no_path in zip.namelist():
                                self.reporter.logger.debug(f'\t{file_no_path} archived successfully.')
                            #if file was not added to archive
                            else:
                                self.reporter.logger.error(f'\t{file_no_path} failed to archive.')
                                all_files_archived = False
                                continue
                            #remove original file
                            os.remove(f'{file}')
                            action_count += 1
                        zip.close()
                else:
                    self.reporter.logger.error(f'\t{file} does not exist, skipping...')
                    all_files_archived = False
        self.reporter.logger.info(f'{action_count} files archived.')
        self.reporter.logger.debug(f'all_files_archived: {all_files_archived}')
        return all_files_archived

    #organize files based on CLI args
    def organize_files(self):
        """
        Organizes files based on CLI args
        if --move-files is passed, files are moved to category folders within target directory
        if --archive-files is passed, files are archived to category zip files within target directory
        if --remove-duplicates is passed, duplicate files are removed
        """
        duplicates_removed_success = True
        files_archived_success = True
        files_moved_sucess = True
        
        if self._remove_duplicates:
            duplicates_removed_success = self.remove_duplicates_files()
        
        if self._archive_files:
            files_archived_success = self.archive_files(self.fetcher.create_file_dictionary(self.fetcher.get_file_list()))
        elif self._move_files:
            files_moved_sucess = self.move_files(self.fetcher.create_file_dictionary(self.fetcher.get_file_list()))
        
        self.reporter.logger.debug(f'duplicates_removed_success: {duplicates_removed_success}')
        self.reporter.logger.debug(f'files_archived_success: {files_archived_success}')
        self.reporter.logger.debug(f'files_moved_sucess: {files_moved_sucess}')
        self.reporter.logger.debug(f'all operations successful: {duplicates_removed_success and files_archived_success and files_moved_sucess}')

        return {"duplicate_files_removed": duplicates_removed_success,
                "files_archived": files_archived_success,
                "files_moved_success": files_moved_sucess,
                "all": duplicates_removed_success and files_archived_success and files_moved_sucess}


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
                                         
    
    def __init__(self, target_directory, move_mode, archive_mode, remove_duplicates_mode, log_level=logging.INFO, data_fetcher=None):
        # CLI args...
        self._dry_move = move_mode
        self._dry_archive = archive_mode
        self._dry_remove_duplicates = remove_duplicates_mode        
        
        # logging setup
        self.logger = logging.getLogger("system_logger")
        self.logger.setLevel(log_level)
        self.handler = logging.StreamHandler()
        #self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s  %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        # data fetcher setup
        self.fetcher = data_fetcher

    # simulate moving files
    def dry_move(self, file_dict):
        # TODO test
        target_directory = self.fetcher.get_target_directory() #type: ignore
        
        all_files_moved = True

        folders_created = 0
        #Simulate creating folders
        for file_category in file_dict.keys():
            if not os.path.exists(f'{target_directory}/{file_category}'):
                self.logger.info(f'Creating {file_category} folder...')
                folders_created += 1
        file_count = sum(len(value) for value in file_dict.values())
    
        self.logger.info(f'Moving {file_count} files...')

        action_count = 0

        for file_category, file_list in file_dict.items():
        
            self.logger.info(f'Moving {len(file_list)} file(s) to {file_category}...')
            for file in file_list:
                file_no_path = os.path.basename(file)

                if os.path.isdir(f'{file}'):
                    self.logger.error(f'{file} is a directory, skipping...')
                #ensure file still exists
                if os.path.exists(f'{file}'):

                    self.logger.info(f'\tMoving {file_no_path}...')

                    # check if file is already present in target directory
                    #TODO remove this check
                    self.logger.info(f'\tMoved {file_no_path} to {file_category}.')
                    action_count += 1
                else:
                    self.logger.error(f'\t{file} does not exist, skipping...')
                    all_files_moved = False

        self.logger.info(f'Dry run complete. {folders_created} folders would be created. {action_count} files would be moved.')
        self.logger.info(f'All file operations successful: {all_files_moved}\n')
        return all_files_moved

    # simulate archiving files
    def dry_archive(self, file_dict):
        # TODO test
            # run after real run with new files
        target_directory = self.fetcher.get_target_directory()#type: ignore
        all_files_archived = True
        prefix = "Dry run: "
        archives_created = 0
        #Simulate creating archives
        for file_category in file_dict.keys():
            if not os.path.exists(f'{target_directory}/{file_category}.zip'):
                self.logger.info(f'Creating {file_category}.zip...')
                archives_created += 1
        file_count = sum(len(value) for value in file_dict.values())
    
        self.logger.info(f'Archiving{file_count} files...')

        action_count = 0

        for file_category, file_list in file_dict.items():
            self.logger.info(f'Archiving {len(file_list)} file(s) to {file_category}.zip...')
            for file in file_list:
                file_no_path = os.path.basename(file)
                #ensure file still exists
                if os.path.exists(f'{file}'):
                    self.logger.info(f'\tArchiving {file_no_path}...')
                    
                    #check if zip file exists
                    if os.path.exists(f'{target_directory}/{file_category}.zip'):
                    # check if file is already present in archive
                        with zipfile.ZipFile(f'{target_directory}/{file_category}.zip', 'r') as zip:
                            if file_no_path in zip.namelist():
                                print(f'\t{file_no_path} already exists in {file_category}.zip. Skipping...')
                                all_files_archived = False
                                zip.close()
                                continue
                            else:
                                self.logger.info(f'\tArchived {file_no_path} to {file_category}.zip.')
                                self.logger.info(f'\tRemoved original file: {file_no_path}.')
                                action_count += 1
                                zip.close()
                    else:
                        self.logger.info(f'\tArchived {file_no_path} to {file_category}.zip.')
                        self.logger.info(f'\tRemoved original file: {file_no_path}.')
                        action_count += 1
                else:
                    self.logger.error(f'\t{file} does not exist, skipping...')
                    all_files_archived = False

        self.logger.info(f'Dry run complete. {archives_created} archives would be created. {action_count} files would be archived.')
        self.logger.info(f'All file operations successful: {all_files_archived}\n')
        return all_files_archived

    # simulate duplicate discovery/removal/renaming
    def dry_remove_duplicates(self):
        #TODO test
        prefix = "Dry run: "
        duplicates, orphaned_duplicates = self.fetcher.get_duplicate_files(self.fetcher.file_list)#type: ignore
        
        files_removed = 0

        if len(duplicates) == 0:
            self.logger.info("No duplicates found.")
            return
        else:
            #simulate renaming orphaned duplicates
            if self.fetcher.settings['rename_orphaned_duplicates'] == True:#type: ignore

                self.logger.info(f'{prefix}Renaming {len(orphaned_duplicates)} orphaned duplicates...')

                for file, pattern in orphaned_duplicates:
                    
                    if os.path.isfile(file):
                                                
                        new_filename = self.fetcher.strip_duplicate_pattern(file, pattern)#type: ignore
                        file = os.path.basename(file)
                        new_filename = os.path.basename(new_filename)
                        self.logger.info(f'\tRenaming {file} to: {new_filename}...')
            
            #simulate removing duplicates
            self.logger.info(f'{prefix}Removing {len(duplicates)} duplicate files...')
            for file in duplicates:
                if os.path.isfile(file):
                    self.logger.info(f'\tRemoving {file.split("/")[-1]}...')
                    files_removed += 1

        self.logger.info(f'Dry run complete. {files_removed} files would be removed.\n')

    # orchestrate dry run
    def dry_run(self):
        #TODO make dry run results persistent across dry runs, 
        #     i.e. files removed/renamed by dry_remove_duplicates should not appear in subsequent dry runs
        #TODO make messaging more consistent

        if self._dry_remove_duplicates:
            self.dry_remove_duplicates()
        if self._dry_archive:
            self.dry_archive(self.fetcher.create_file_dictionary(self.fetcher.get_file_list()))#type: ignore
        elif self._dry_move:
            self.dry_move(self.fetcher.create_file_dictionary(self.fetcher.get_file_list()))#type: ignore
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


        reporter.logger.info("Starting...\n")

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
            reporter.logger.info("Finished without errors.")
        else:
            reporter.logger.error("Finished with errors.")

# main
if __name__ == '__main__':

    main = Main()
    main.run()