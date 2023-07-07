import os
import zipfile
import shutil
import re


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

