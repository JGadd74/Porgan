import os
import logging
import zipfile




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
    