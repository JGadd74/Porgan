"""This module is responsible for fetching data for other modules."""
import os
import sys
import hashlib
import re
import yaml

class DataFetcher:
    """
        This class loads and fetches data for other classes.
        """
    def __init__(self, file_io_reporter, settings_file, path_to_extensions_file, target_directory = None, custom_mode = False):
        """
            parameters:
               - file_io_reporter (object) - the file_io_reporter object to use for logging
               - settings_file (str) - the settings file to get the default target directory from
               - extensions_file (str) - the extensions file to get the extensions dictionary from
               - target_directory (str) - the target directory to overwrite the default target directory
        """
        self._new_target_directory = ''
        self.reporter = file_io_reporter
        self.settings = self._load_yaml(settings_file)
        self.extensions_dictionary = self._load_yaml(path_to_extensions_file)
        self._set_target_directory(target_directory)
        self.file_list = self.get_file_list() # type: list[str]
        self.new_file_extensions = [] # type: list[str]
        self.custom_mode = custom_mode # type: bool
        
        self.default_extensions_dictionary = self.settings['default_extensions'] # type: str
        self.custom_extensions_dictionary = self.settings['custom_extensions'] # type: str

    def _get_custom_extensions_dictionary(self, custom_extensions_file) -> dict:
        
        if custom_extensions_file is not None:
            if os.path.isfile(custom_extensions_file):
                return self._load_yaml(custom_extensions_file)
            
            self.reporter.logger.error("Custom extensions file not found at path:", custom_extensions_file)
            self.reporter.logger.error("Exiting...")
            sys.exit()
        else:
            if self.settings['custom_extensions'] is not None:
                if os.path.isfile(self.settings['custom_extensions']):
                    return self._load_yaml(self.settings['custom_extensions'])
                
                self.reporter.logger.error("Custom extensions file not found at path:", self.settings['custom_extensions'])
                self.reporter.logger.error("Exiting...")
                sys.exit()
            else:
                self.reporter.logger.error("No custom extensions file found.")
                self.reporter.logger.error("Exiting...")
                sys.exit()

    def _load_yaml(self, path_to_file) -> dict:
        """
        Loads a yaml file and returns its contents.
        
        parameters: path_to_file (str) - the path to the yaml file to load  
        
        returns: the contents of the yaml file
        """
        if path_to_file is None:
            self.reporter.logger.error("path_to_file is None")
            self.reporter.logger.error("Exiting...")
            sys.exit()
        try:
            with open(path_to_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.reporter.logger.error("FileNotFoundError: File not found at path:", path_to_file)
            self.reporter.logger.error("Exiting...")
            sys.exit()
    
    def _set_target_directory(self, target_directory = None) -> None:
        """
        Sets the target directory. If a target directory is provided as an argument and it exists,
        it will be used as the new target directory. Otherwise, the default target directory from the settings file will be used.

        Parameters: target_directory (str): The target directory to set as the new target directory. If None, the default target directory from the settings file will be used.

        Returns: None
        """
        if target_directory is not None and os.path.isdir(target_directory) and os.path.exists(target_directory):
            self.reporter.logger.info(f"Target directory set to: {target_directory}")
            self._new_target_directory = target_directory
        else:
            #load default target directory from settings file
            self.reporter.logger.debug("loading default target directory from settings file...")
            self._new_target_directory = self.settings['target_directory']
    
    def get_app_made_zips(self) -> list:
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
        zips.append('unknowns.zip')
        return zips
    
    def get_app_made_folders(self) -> list:
        """
        This function returns a list of folder names from the extensions dictionary.
        this is used to prevent the app from moving/zipping its own folders.

        parameters: none

        returns: a list of folder names from the extensions dictionary
        """
        folder_names = list(self.extensions_dictionary.keys())
        return folder_names

    def get_existing_containers(self) -> tuple:
        """this function returns a tuple of all
            folders and zip files made by 
            this application"""
        
        zips = []
        folders = []

        category_names = list(self.extensions_dictionary.keys())
        category_names.append('unknowns')
        
        #get all items in target directory
        for item in os.listdir(self._new_target_directory):
            #used for determining item type (dir/file) checking
            item_with_path = os.path.join(self._new_target_directory, item)
            if os.path.isdir(item_with_path):
                if item in category_names:
                    self.reporter.logger.debug(f"found folder: {item}")
                    folders.append(item_with_path)
                    continue

            if os.path.isfile(item_with_path):
                item_without_extension = os.path.basename(os.path.splitext(item)[0])
                if item_without_extension in category_names and item.endswith('.zip'):
                    self.reporter.logger.debug(f"found zip: {item}")
                    zips.append(item_with_path)
            
            
                
        return zips, folders
    
    def get_file_list(self) -> list:
        """This function returns a list of all files as absolute paths in the target directory."""
        files = []
        if self._new_target_directory == '':
            self.reporter.logger.error("No target directory provided. Exiting...")

        for item in os.listdir(self._new_target_directory):
            if  os.path.isfile(os.path.join(self._new_target_directory,item)) and item not in self.get_app_made_zips():
                files.append(os.path.abspath(os.path.join(self._new_target_directory, item)))
        
        return files

    def strip_regex_pattern(self, file, pattern) -> str:
        """This function strips the given regex pattern from the given file name."""
        new_filename = re.sub(pattern, "", file)
        new_filename = new_filename.replace(" ", "")
        return new_filename
    
    def get_duplicate_files(self, file_list) -> tuple:
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

        for filename in self.get_file_list():
            # Check each pattern
            for pattern in patterns:
                #match = pattern.match(filename)
                match = re.search(pattern, filename)
                # If there is a match, and the original file exists, add it to the list
                if match and self.strip_regex_pattern(filename, pattern) in file_list:
                    # if there is a match, and the original exists, add duplicate file to the return list

                    duplicate_files.append(filename)
                    filename = os.path.basename(filename)
                    self.reporter.logger.debug(f'duplicate: {filename} \n\t\t\t original:  {self.strip_regex_pattern(filename, pattern)}\n')
                    break
                if match:
                    matches_with_no_original.append((filename, pattern))
                    filename = os.path.basename(filename)
                    self.reporter.logger.debug(f'Orphan duplicate found: {filename}')
        
        return duplicate_files, matches_with_no_original

    def create_file_dictionary(self, file_list, extensions_dictionary = None) -> dict:
        """
        Creates a dictionary of files where each key is a file category and the value is a list of the files that belong to that category.
        Saves a list of previously unknown file extensions to self.new_file_extensions. Currently unused. TODO use this to update the extensions dictionary.

            parameters: file_list (list): A list of file paths.
            extensions_category_list (list): A dictionary where each key is a file category and the value is a list of file extensions that belong to that category.

        Returns:
            dict: A dictionary where each key is a file category and the value is a list of file paths that belong to that category. Files with unknown file extensions are categorized as 'unknown'.
        """
        
        if extensions_dictionary is None:
            extensions_dictionary = self.extensions_dictionary

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
            for key, val in extensions_dictionary.items():
                for ext in val:
                    if file.lower().endswith(f'.{ext.lower()}'):
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
    
    def create_custom_file_dictionary(self, file_list, extensions_dictionary):
        # run create_file_dictionary(file_list, extensions_dictionary)
        #split dictionary returned into two dictionaries
        #one with known extensions, one with unknown extensions
        #the unknown are extensions that didn't match the custom dictionary
        #pass unknowns to create_file_dictionary(unknowns_files) no dictionary to use default
        #combine the two dictionaries
        #return the combined dictionary

        #TODO tesssstttttt
        
        base_dict = self.create_file_dictionary(file_list, extensions_dictionary)
        unknowns = base_dict.pop('unknowns')
        default_dict = self.create_file_dictionary(unknowns)
        base_dict.update(default_dict)
        return base_dict

    def get_target_directory(self) -> str:
        """This function returns the target directory."""
        return self._new_target_directory
    
    def hash_file(self, file_path) -> str:
        """This function returns the sha256 hash of the given file."""
        with open(file_path, 'rb') as file:
            return hashlib.sha256(file.read()).hexdigest()

    def compare_files(self, file1_path, file2_path) -> bool:
        """This function compares two files and returns True if they are the same and 
        False if they are different."""
        return self.hash_file(file1_path) == self.hash_file(file2_path)
    
    def verify_extraction(self, filename) -> bool:
        """This function takes a filename and verifies that it was extracted correctly.
        It does this by comparing the hash of the file in the target directory with the 
        hash of the file in the source directory. If the hashes match, the file was extracted
        correctly. If they don't match, the file was not extracted correctly.
        """

        for file in self.get_file_list():
            if filename in file:
                filename_with_path = os.path.join(self._new_target_directory, filename)
                if self.compare_files(file, filename_with_path):
                    return True
                return False
        return False
