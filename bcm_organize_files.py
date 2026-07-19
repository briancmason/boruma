from pathlib import Path
import argparse
import shutil


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Organize files by type.")
    parser.add_argument("directory", help="Directory to organize")
    parser.add_argument("--apply", action="store_true", help="Actually move files")
    return parser.parse_args(argv)


def organize(source: Path, apply: bool) -> tuple[int, int]:
    moved = 0
    skipped = 0
    for file in iter_target_files(source):
        folder_name = category_for(file)
        dest_dir = source / folder_name
        dest = unique_destination(dest_dir, file.name)
        if apply:
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(file), str(dest))
            print(f"Moved {file.name} -> {folder_name}/{dest.name}")
        else:
            print(f"Would move {file.name} -> {folder_name}/{dest.name}")
        moved += 1
    return moved, skipped


CATEGORIES = {
    ".png": "Images",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".pdf": "Documents",
}
FALLBACK_FOLDER = "Other"


def category_for(path: Path) -> str:
    return CATEGORIES.get(path.suffix.lower(), FALLBACK_FOLDER)


def unique_destination(dest_dir: Path, name: str) -> Path:
    dest = dest_dir / name
    stem = dest.stem
    suffix = dest.suffix
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return dest


def iter_target_files(source: Path) -> list[Path]:
    files = []
    for entry in source.iterdir():
        if entry.is_dir():
            continue          # skip folders
        if entry.name.startswith("."):
            continue          # skip hidden files
        files.append(entry)   # keep this one
    return files


def main(argv=None):
    args = parse_args(argv)
    source = Path(args.directory).expanduser()
    if not source.is_dir():
        print(f"Not a directory: {source}")
        return 1
    if not args.apply:
        print("DRY RUN — no files will be moved. Use --apply to commit.")
    moved, skipped = organize(source, args.apply)
    verb = "Moved" if args.apply else "Would move"
    print(f"Done. {verb} {moved} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())