from pathlib import Path
from collections import Counter

# Point this to your eu_legislation directory.
EU_LEGISLATION_DIR = Path("C:\\Users\\Roxas\\OneDrive\\Desktop\\Project_Space\\eu_legislation")

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
}


def count_images(image_dir: Path) -> tuple[int, Counter]:
    """Count image files recursively inside one image directory."""
    counts_by_extension = Counter()

    if not image_dir.exists():
        return 0, counts_by_extension

    for path in image_dir.rglob("*"):
        if path.is_file():
            suffix = path.suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                counts_by_extension[suffix] += 1

    return sum(counts_by_extension.values()), counts_by_extension


def inspect_corpus_images(corpus_dir: Path):
    if not corpus_dir.exists():
        raise FileNotFoundError(
            f"Corpus directory does not exist: {corpus_dir}"
        )

    batch_dirs = sorted(
        path
        for path in corpus_dir.iterdir()
        if path.is_dir() and path.name.startswith("batch_")
    )

    if not batch_dirs:
        print(f"No batch directories found under: {corpus_dir}")
        return

    grand_total = 0
    grand_extensions = Counter()

    print("=" * 70)
    print("JURISYNTH IMAGE CORPUS INSPECTION")
    print("=" * 70)

    for batch_dir in batch_dirs:
        image_dir = batch_dir / "image_store"

        batch_total, extension_counts = count_images(image_dir)

        grand_total += batch_total
        grand_extensions.update(extension_counts)

        print(
            f"{batch_dir.name}: "
            f"{batch_total:,} images"
        )

        if batch_total == 0:
            if image_dir.exists():
                print("  image_store exists but contains no recognized images")
            else:
                print("  image_store missing")

    print()
    print("=" * 70)
    print(f"TOTAL IMAGES: {grand_total:,}")
    print("=" * 70)

    if grand_extensions:
        print("\nBy extension:")

        for extension, count in grand_extensions.most_common():
            print(f"  {extension:<6} {count:,}")


if __name__ == "__main__":
    inspect_corpus_images(EU_LEGISLATION_DIR)