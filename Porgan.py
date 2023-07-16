"""This module is the main module for the Porgan program. It is responsible for
getting arguments from the command line, creating instances of FileIOReporter,
DataFetcher and FileOrganizer, and running the program."""
import argparse
import logging
import os
from modules.data_fetcher import DataFetcher
from modules.file_io_reporter import FileIOReporter
from modules.file_organizer import FileOrganizer

  
class Main:
    """
    gets arguments from command line
    creates instances of FileIOReporter, DataFetcher and FileOrganizer
    has run() method that runs the program
    """

    def __init__(self):
        #get arguments from command line
        parser = argparse.ArgumentParser(description='Organizes files by removing or renaming duplicate files and/or archiving, or moving files to their respective folders based on their file extension.')
        # Define the arguments...
        parser.add_argument('-a', '--archive', action='store_true',
                            help='Archives files to their respective zip files based on their file extension.')
        parser.add_argument('-m', '--move', action='store_true',
                            help='Moves files to their respective folders based on their file extension.')
        parser.add_argument('-d', '--rm-duplicates', action='store_true',
                            help='Remove duplicate files.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Simulate running the program without actually moving/removing files')
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='Displays verbose output')
        parser.add_argument('-t', '--target', type=str,
                            help='Target directory to organize. Default is /home/user/Downloads')
        parser.add_argument('-u', '--unpack', nargs='*', default=False,
                            help='Unpacks all previously sorted archives/folders in the target directory. '
                                 'If specific folders/archives are specified, only those will be unpacked.')
        self.args = parser.parse_args()

    def run(self):
        """this method runs the program"""
        
        reporter = FileIOReporter(  self.args.move,
                                    self.args.archive,
                                    self.args.rm_duplicates,
                                    logging.DEBUG if self.args.verbose else logging.INFO)
        
        path_to_yamls = os.path.dirname(os.path.abspath(__file__)) + "/etc"

        fetcher = DataFetcher(file_io_reporter=reporter,
                                settings_file=f'{path_to_yamls}/Settings.yaml',
                                path_to_extensions_file=f'{path_to_yamls}/Extensions.yaml',
                                target_directory=self.args.target)
        
        reporter.fetcher = fetcher

        organizer = FileOrganizer(file_io_reporter=reporter,
                                    data_fetcher=fetcher,
                                    archive=self.args.archive,
                                    move=self.args.move,
                                    remove_duplicates=self.args.rm_duplicates)
        
        operations_ran_without_error = True
        
        reporter.logger.info("Starting...")
        
        if self.args.dry_run:
            reporter.dry_run()
        elif self.args.archive and self.args.move:
            reporter.logger.error("Cannot archive and move at the same time. Please choose one or the other.")
            operations_ran_without_error = False
        else:
            if isinstance(self.args.unpack, list):
                if len(self.args.unpack) == 0:
                    organizer.unpack()
                else:
                    organizer.unpack(self.args.unpack)
            operations_ran_without_error = organizer.organize_files()["all"]

        if operations_ran_without_error:
            reporter.logger.info("Finished.")
        else:
            reporter.logger.error("Finished with errors.")

    # main
if __name__ == '__main__':
    main = Main()
    main.run()
