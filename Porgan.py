import argparse
import logging

from modules.DataFetcher import DataFetcher
from modules.FileIOReporter import FileIOReporter
from modules.FileOrganizer import FileOrganizer

  
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
        parser.add_argument('-t', '--target', type=str, help='Target directory to organize. Default is /home/user/Downloads')
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