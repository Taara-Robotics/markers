import argparse
import os
import time
import zipfile

args_parser = argparse.ArgumentParser()
args_parser.add_argument("-l", "--large", type=int, required=False, default=0, help="Number of 270mm markers to select")
args_parser.add_argument("-m", "--medium", type=int, required=False, default=0, help="Number of 144mm markers to select")
args_parser.add_argument("-s", "--small", type=int, required=False, default=0, help="Number of 90mm markers to select")
args = args_parser.parse_args()

# Define PDF source paths for each marker size
root = os.path.join(os.path.dirname(__file__), "..")

pdf_sources = {
    "size_270mm": os.path.join(root, "apriltags/tagStandard41h12/pdf/270mm"),
    "size_144mm": os.path.join(root, "apriltags/tagStandard41h12/pdf/144mm"),
    "size_90mm": os.path.join(root, "apriltags/tagStandard41h12/pdf/90mm"),
}

# Go through files in "used" folder to get list of filenames that are already used
# each file contains one filename per line
used_filenames = set()

for filename in os.listdir("./used"):
    with open(os.path.join("./used", filename), "r") as f:
        for line in f:
            used_filenames.add(line.strip())

# Select marker filenames based on user input
# group by size
selected_filenames = {
    "size_270mm": [],
    "size_144mm": [],
    "size_90mm": [],
}

for size, count in [("size_270mm", args.large), ("size_144mm", args.medium), ("size_90mm", args.small)]:
    if count > 0:
        source_folder = pdf_sources[size]
        available_files = [
            f for f in os.listdir(source_folder)
            if f.endswith(".pdf") and f not in used_filenames
        ]
        selected = available_files[:count]
        selected_filenames[size].extend(selected)

        # print warning if not enough files are available
        if len(selected) < count:
            print(f"Warning: Requested {count} files for {size}, but only {len(selected)} available.")

# Print selected filenames
for size in ["size_270mm", "size_144mm", "size_90mm"]:
    for filename in selected_filenames[size]:
        print(f"{size}: {filename}")

# Write selected filenames to "used" folder
# one file for all filenames with comments separating sizes
# filename format: used_YYYY_MM_DD_HH_MM_SS.txt
timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
used_filename = os.path.join("./used", f"used_{timestamp}.txt")

with open(used_filename, "w") as f:
    for size in ["size_270mm", "size_144mm", "size_90mm"]:
        f.write(f"# {size} markers\n")
        for filename in selected_filenames[size]:
            f.write(f"{filename}\n")
        f.write("\n")

# Create a zip file containing the selected PDFs
# group by size in separate folders within the zip
zip_filename = f"selected_markers_{timestamp}.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for size in ["size_270mm", "size_144mm", "size_90mm"]:
        source_folder = pdf_sources[size]
        for filename in selected_filenames[size]:
            file_path = os.path.join(source_folder, filename)
            zipf.write(file_path, arcname=os.path.join(size, filename))