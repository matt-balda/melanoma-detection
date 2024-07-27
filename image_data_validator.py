import os
from pathlib import Path
from typing import List
from PIL import Image
from PIL.ExifTags import TAGS
import hashlib

class ImageDataValidator:
    """
    A class to validate and verify image data, as well as inconsistency and associated metadata.

    Parameters:
    images_dir (List[str]): List of directory paths containing image files.
    width (int): Expected width of the images.
    height (int): Expected height of the images.
    extensions (List[str]): List of valid image file extensions.

    Attributes:
    images_dir (List[str]): List of directory paths to scan for images.
    ver_width (int): Expected width of the images.
    ver_height (int): Expected height of the images.
    ver_extensions (List[str]): List of acceptable image file extensions.
    sizes (List[int]): List to store sizes of directories.
    images_hashes (dict): Dictionary mapping image hashes to file names.
    duplicates (List[dict]): List to store information about duplicate images.
    inconsistencies (List[dict]): List to record any issues or inconsistencies found.
    dimensions (List[dict]): List to store metadata about image dimensions.
    images (dict): Dictionary mapping file paths to file names for all valid images.

    Methods:

    OBS: example of required directory, list with 1 directory or more
    ['./name/test/class1',
     './name/test/class2',
     './name/train/class1',
     './name/train/class2']
    
    """
    def __init__(self, images_dir:List[str], width:int, height:int, extensions:List[str]):
        self.images_dir = images_dir
        self.ver_width = width
        self.ver_height = height
        self.ver_extensions = extensions
        self.sizes = []
        self.images_hashes = {}
        self.duplicates = []
        self.inconsistencies = []
        self.dimensions = []
        self.images = self._load_images()

    def _load_images(self):
        """
        Loads images from specified directories, performing checks and recording inconsistencies.

        This method iterates through directories listed in `self.images_dir`, verifying each directory
        for file presence. For each image file, it performs various checks (extension, quality, metadata,
        and dimensions) and records any issues found. It also identifies duplicate images and updates 
        the internal state with the size of each directory and a mapping of file paths to file names.

        Returns:
        dict: A dictionary mapping file paths to file names for all valid images found.

        Notes:
        - Updates `self.sizes` with a dictionary of directory sizes.
        - Appends inconsistencies to `self.inconsistencies` for files that fail checks.
        - Uses methods `check_extension`, `check_quality`, `check_metadata`, `check_dimension`,
        and `find_duplicate_images` for various validations.
        """

        images = {}
        sizes_wrapper = {}

        for directory in self.images_dir: 
            if self.__check_directory_file(directory): 
                sizes_wrapper[directory] = len(os.listdir(directory))

                for filename in os.listdir(directory):
                    path = os.path.join(directory, filename)
                    class_name = directory  

                    if not self.check_extension(path, self.ver_extensions):
                        self.inconsistencies.append({
                            'file_path': path,
                            'error': 'Invalid extension',
                            'issue': 'Extension check failed'
                        })
                        #continue

                    if not self.check_quality(path):
                        self.inconsistencies.append({
                            'file_path': path,
                            'error': 'Corrupted or empty file',
                            'issue': 'Quality check failed'
                        })
                        #continue

                    if not self.check_metadata(path):
                        self.inconsistencies.append({
                            'file_path': path,
                            'error': 'No metadata',
                            'issue': 'Metadata check failed'
                        })
                        self.create_metadata(path)
                        #continue

                    if not self.check_dimension(path, self.ver_width, self.ver_height):
                        self.inconsistencies.append({
                            'file_path': path,
                            'error': 'Dimension mismatch',
                            'issue': 'Dimension check failed'
                        })
                        #continue
                        
                    images[path] = filename
                    self.find_duplicate_images(path, filename, class_name)

        self.sizes = sizes_wrapper
        return images

    def __check_directory_file(self, directory):
        """
        Checks if a given directory contains any files.

        Parameters:
        directory (str): Path to the directory to check.

        Returns:
        bool:
            - True if the directory contains at least one file.
            - False if the directory is empty or if the path is invalid.

        Raises:
        ValueError:
            - If the directory does not exist.
            - If the path is not a directory.

        Notes:
        - Uses the `Path` class from the `pathlib` module to verify directory existence and type.
        """
    
        path = Path(directory)
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        return any(file.is_file() for file in path.iterdir())

    def check_extension(self, file_path: str, type_extension: List[str]):
        """
        Checks if an image file has one of the specified file extensions.

        Parameters:
        file_path (str): Path to the image file.
        type_extension (List[str]): List of valid image formats (extensions) to check against.

        Returns:
        bool: 
            - True if the image format matches one of the specified extensions.
            - False if the format does not match or if an error occurs while opening the file.

        Notes:
        - The method checks the image format using the `PIL.Image.format` attribute and compares it against the provided list.
        """

        try:
            with Image.open(file_path) as img:
                return img.format.lower() in (type_extension)
        except IOError:
            return False
        
    def check_quality(self, file_path: str):
        """
        Checks if an image file is of good quality by verifying its file size and integrity.

        Parameters:
        file_path (str): Path to the image file.

        Returns:
        bool: 
            - True if the file size is greater than 0 and the image integrity is verified.
            - False if the file size is 0 or if an error occurs during verification.

        Notes:
        - Uses `os.stat` to check the file size and `PIL.Image.verify` to check image integrity.
        """

        try:
            statfile = os.stat(file_path)
            filesize = statfile.st_size
        
            if filesize == 0: return False

            with Image.open(file_path) as img:
                img.verify() 

            return True
        except (IOError, SyntaxError) as e:
            return False

    def check_metadata(self, file_path: str):
        """
        Checks if an image file contains EXIF metadata.

        Parameters:
        file_path (str): Path to the image file.

        Returns:
        Tuple[bool, Optional[dict]]
            - True and a dictionary of EXIF data if metadata is present.
            - False if metadata is not present or an error occurs.

        Notes:
        - Returns False if the file cannot be opened or if EXIF data is missing.
        """

        try:
            with Image.open(file_path) as img:
                exif = img._getexif()
                if exif is None: return False
                return True, exif
        except (IOError, SyntaxError) as e:
            return False
        
    def create_metadata(self, file_path: str):
        """
        Creates and stores metadata for an image based on its dimensions and class.

        Parameters:
        file_path (str): Path to the image file.

        Returns:
        None
            If successful, the method does not return a value.
        Exception
            If an error occurs while opening the file, the exception is returned.

        Notes:
        - Metadata includes the image name, width, height, and the class derived from the file path.
        - The image class is extracted as the parent directory of the file path.
        """
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                self.dimensions.append({
                    'image_name': os.path.basename(file_path),
                    'width': width,
                    'height': height,
                    'class': file_path.split('/')[-2]
                })
            return None
        except (IOError, SyntaxError) as e:
            return e
        
    def check_dimension(self, file_path: str, width: int, height: int):
        """
        Checks if the dimensions of an image match the specified width and height.

        Parameters:
        file_path (str): Path to the image file.
        width (int): Expected width of the image.
        height (int): Expected height of the image.

        Returns:
        bool: True if the image dimensions match the specified width and height, otherwise False.

        Notes:
        - Returns False if the file cannot be opened or the image format is incorrect.
        """

        try:
            with Image.open(file_path) as img:
                w, h = img.size
                return w == width and h == height
        except (IOError, SyntaxError) as e:
            return False
        
    def __calculate_md5(self, file_path:str):
        """
        Computes the MD5 hash of a file.

        Parameters:
        file_path (str): Path to the file for which the MD5 hash is calculated.

        Returns:
        str: The hexadecimal MD5 hash of the file.

        Notes:
        - The method reads the file in binary mode in chunks of 4096 bytes.
        """

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def find_duplicate_images(self, file_path: str, file_name: str, class_name: str):
        """
        Checks for and records duplicate images based on their MD5 hash.

        Parameters:
        file_path (str): Path to the image file.
        file_name (str): Name of the image file.
        class_name (str): Class/category of the image.

        Returns:
        None
            If an exception occurs, it will be returned.

        Notes:
        - `images_hashes` is a dictionary storing image hashes and names.
        - `duplicates` is a list of dictionaries recording duplicate images.
        """

        try:
            image_hash = self.__calculate_md5(file_path)
            if image_hash in self.images_hashes:
                self.duplicates.append({
                    'image_name': file_name,
                    'class': class_name,
                    'duplicate_of': self.images_hashes[image_hash]
                })
            else:
                self.images_hashes[image_hash] = file_name
        except Exception as e:
            return e
