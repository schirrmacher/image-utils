import os
import argparse
from typing import Set, Dict, List


def get_files_by_basename(folder_path: str) -> Dict[str, List[str]]:
    basename_dict = {}
    for f in os.listdir(folder_path):
        full_path = os.path.join(folder_path, f)
        if os.path.isfile(full_path):
            basename, _ = os.path.splitext(f)
            basename_dict.setdefault(basename, []).append(f)
    return basename_dict


def get_files_in_folder(folder_path: str) -> Set[str]:
    return {
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    }


def compare_folders(
    folder_a: str, folder_b: str, ignore_extension: bool, reverse: bool
) -> Set[str]:
    if reverse:
        source_folder, target_folder = folder_b, folder_a
    else:
        source_folder, target_folder = folder_a, folder_b

    if ignore_extension:
        source_dict = get_files_by_basename(source_folder)
        target_dict = get_files_by_basename(target_folder)

        source_basenames = set(source_dict.keys())
        target_basenames = set(target_dict.keys())

        diff_basenames = source_basenames - target_basenames
        diff_files = set()
        for bname in diff_basenames:
            diff_files.update(source_dict[bname])
        return diff_files
    else:
        source_files = get_files_in_folder(source_folder)
        target_files = get_files_in_folder(target_folder)
        return source_files - target_files


def delete_files(files: Set[str], folder_path: str) -> None:
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.exists(file_path):
            print(f"Deleting {file_path}")
            os.remove(file_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare files between two folders.")
    parser.add_argument("folder_a", type=str, help="Path to folder A")
    parser.add_argument("folder_b", type=str, help="Path to folder B")
    parser.add_argument(
        "--ignore-extension",
        "-ir",
        action="store_true",
        help="Ignore file extensions while comparing names",
    )
    parser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="Delete files in the 'difference' folder",
    )
    parser.add_argument(
        "--reverse",
        "-r",
        action="store_true",
        help="Reverse the order of comparison (compare B to A)",
    )

    args = parser.parse_args()

    # Determine the source folder based on reverse flag for deletion purposes.
    source_folder = args.folder_b if args.reverse else args.folder_a

    diff_files = compare_folders(
        args.folder_a, args.folder_b, args.ignore_extension, args.reverse
    )

    if diff_files:
        if args.reverse:
            print(f"Files in {args.folder_b} but not in {args.folder_a}:")
        else:
            print(f"Files in {args.folder_a} but not in {args.folder_b}:")

        for file in sorted(diff_files):
            print(file)

        if args.delete:
            delete_files(diff_files, source_folder)
    else:
        if args.reverse:
            print(f"All files in {args.folder_b} are available in {args.folder_a}.")
        else:
            print(f"All files in {args.folder_a} are available in {args.folder_b}.")


if __name__ == "__main__":
    main()
