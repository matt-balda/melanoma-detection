import os
import cv2
import csv
import pandas as pd
import imghdr
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import opendatasets as od

from PIL import Image

od.download("https://www.kaggle.com/datasets/bhaveshmittal/melanoma-cancer-dataset")

base_dir = "./DATA/"

directories = [
    f"{base_dir}test/Benign",
    f"{base_dir}test/Malignant",
    f"{base_dir}train/Benign",
    f"{base_dir}train/Malignant"
]

def is_valid_image_pillow(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
    
for directory in directories:
    print(f"Verifying images in directory: {directory}")
    file_names = os.listdir(directory)
    
    for file_name in file_names:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith(('.jpg', '.jpeg')):
            print(f"File: {file_name}")
            print("Is valid image:", is_valid_image_pillow(file_path))
        else:
            print(f"Skipping non-image file: {file_name}")
        print() 
    print()