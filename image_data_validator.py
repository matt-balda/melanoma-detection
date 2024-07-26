import os
from pathlib import Path

import cv2
import pandas as pd
from PIL import Image
import numpy as np

class ImageDataValidator:
     
    """
    A class for validating images data and associated metadata.

    Attributes:

    Methods:

    OBS: example of required directory, list with 1 directory or more

    ['./name/test/class1',
     './name/test/class2',
     './name/train/class1',
     './name/train/class2']
    """
    def __init__(self, info_file=None, images_dir=None):
        self.info_file = info_file
        self.images_dir = images_dir or []
        self.images = self._load_images()
    
    def __check_directory_file(self, directory):
        """
        Description

        Args:
            ..

        Raises:
            ..

        Returns:
            ..
        """
        path = Path(directory)
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        return any(file.is_file() for file in path.iterdir())

    def _load_images(self):
        images = {}
        for directory in self.images_dir: 
            if self.__check_directory_file(directory): 
                for filename in os.listdir(directory):
                    if filename.lower().endswith(('.jpg')):
                        path = os.path.join(directory, filename)
                        images[path] = filename
        return images
