import os
import shutil

# Define paths
BASE_DIR = "C:/Users/Prasad Patil/Downloads/e-waste-project/e-waste-project/data"
TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "val")

# Mapping of old folders to new categories
CATEGORY_MAPPING = {
    "Battery": "Batteries",
    "Mobile": "Mobile & PCBs",
    "PCB": "Mobile & PCBs",
    "Keyboard": "Peripherals",
    "Mouse": "Peripherals",
    "Player": "Peripherals",
    "Printer": "Printers & Screens",
    "Television": "Printers & Screens",
    "Washing Machine": "Large Appliances",
    "Microwave": "Large Appliances"
}

def move_files(src_dir, dest_dir):
    """Move files from old category folders to new category folders."""
    for old_folder, new_folder in CATEGORY_MAPPING.items():
        old_path = os.path.join(src_dir, old_folder)
        new_path = os.path.join(src_dir, new_folder)

        # Create new folder if it doesn't exist
        os.makedirs(new_path, exist_ok=True)

        if os.path.exists(old_path):
            for file in os.listdir(old_path):
                old_file_path = os.path.join(old_path, file)
                new_file_path = os.path.join(new_path, file)

                # Move file
                shutil.move(old_file_path, new_file_path)

            print(f"Moved files from {old_folder} → {new_folder}")

            # Remove old empty folder
            os.rmdir(old_path)

# Move files for both training and validation datasets
move_files(TRAIN_DIR, TRAIN_DIR)
move_files(VAL_DIR, VAL_DIR)

print("✅ All files moved successfully!")
