import logging
import os

class Logger:
    def __init__(self, logfile, class_name) -> None:
        try:
            # Set up logging
            self.log_file = logfile
            self.log_directory, self.log_file_name = os.path.split(logfile)
            
            #logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
            
            # Create a formatter that includes class and method name
           # Get a logger instance
            if class_name is None:
                class_name=__name__

            self.logger = logging.getLogger(class_name)
            self.logger.setLevel(logging.DEBUG)

            # Create a formatter that includes class and method name
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # Create a handler (e.g., a file handler)
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(file_handler)
        
        except Exception as e:
            self.log_error(f"Exception: {str(e)}")

    # Function to log errors
    def log_error(self, message, exc_info=True):
        try:

            self.logger.error(message, exc_info=exc_info)
            
            #self.upload_log()
        except Exception as e:
            print(f"Exception: {str(e)}")
         
    # Function to log warnings
    def log_warning(self, message):
        try:
            self.logger.warning(message)
            
        except Exception as e:
             self.logger.error(f"Exception: {str(e)}")
            
    # Function to log info messages
    def log_info(self, message):
        try:
             self.logger.info(message)
            
        except Exception as e:
             self.logger.error(f"Exception: {str(e)}")
           
    # Function to log fatal messages
    def log_fatal(self, message, exc_info=True):
        try:
             self.logger.fatal(message, exc_info=exc_info)
            
        except Exception as e:
            self.logger.error(f"Exception: {str(e)}")

  