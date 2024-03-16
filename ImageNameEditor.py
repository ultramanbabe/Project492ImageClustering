import os

# Directory containing files
dir_path = 'F:/Project492/Images/17-02-2024 - Copy'

# Character to look for in file names
char_to_find = '$1'

# Iterate over the files in the directory
for filename in os.listdir(dir_path):
    # If the file name contains the specific character
    if char_to_find in filename:
        # Construct new file name by removing the specific character
        new_filename = filename.replace(char_to_find, '')
        # Construct full file paths
        old_file_path = os.path.join(dir_path, filename)
        new_file_path = os.path.join(dir_path, new_filename)
        # Rename the file
        os.rename(old_file_path, new_file_path)