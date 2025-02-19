import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script's directory
VIDEO_DIR = os.path.join(BASE_DIR, "Content Download")
folder_path = VIDEO_DIR

def delete_all_files(folder_path=VIDEO_DIR):
    """Deletes all files in the specified folder but keeps the folder."""
    
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"❌ The folder '{folder_path}' does not exist.")
        return
    
    # Loop through all files and delete them
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):  # Delete files & shortcuts
                os.unlink(file_path)
            elif os.path.isdir(file_path):  # Delete subfolders and contents
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path}: {e}")

    print(f"✅ All files in '{folder_path}' have been deleted.")

