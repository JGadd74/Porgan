import os
import re
import yaml


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
