#!/usr/bin/env python3
"""
Clean up temporary files older than 24 hours.
Run as a cron job or scheduled task.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from app.config import configuration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def cleanup_directory(directory, max_age_hours=24):
    """
    Delete files in the given directory that are older than max_age_hours.
    
    Parameters:
        directory (str): The path to the directory to clean.
        max_age_hours (int): The age in hours beyond which files will be deleted.
    """
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_mtime = os.path.getmtime(filepath)
            if file_mtime < cutoff:
                try:
                    os.remove(filepath)
                    logging.info(f"Deleted: {filepath}")
                except Exception as e:
                    logging.error(f"Error deleting {filepath}: {e}")

def main():
    logging.info(f"Starting cleanup at {datetime.now()}")
    
    if os.path.exists(configuration.UPLOAD_FOLDER):
        logging.info(f"Cleaning uploads: {configuration.UPLOAD_FOLDER}")
        cleanup_directory(configuration.UPLOAD_FOLDER)
    else:
        logging.warning(f"Uploads directory not found: {configuration.UPLOAD_FOLDER}")

    if os.path.exists(configuration.GIF_OUTPUT_DIR):
        logging.info(f"Cleaning GIF outputs: {configuration.GIF_OUTPUT_DIR}")
        cleanup_directory(configuration.GIF_OUTPUT_DIR)
    else:
        logging.warning(f"GIF outputs directory not found: {configuration.GIF_OUTPUT_DIR}")
    
    logging.info("Cleanup completed")

if __name__ == '__main__':
    main()
