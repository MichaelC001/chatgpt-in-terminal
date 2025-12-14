import os
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import List

# Converts each page of a PDF to a PNG image. Tries pdf2image if available, otherwise
# falls back to the pdftoppm CLI if present.


def convert_with_pdf2image(pdf_path, output_dir, max_dim=1000, dpi=200) -> List[str]:
    try:
        from pdf2image import convert_from_path  # type: ignore
    except Exception as e:
        raise ImportError(f"pdf2image not available: {e}")

    images = convert_from_path(pdf_path, dpi=dpi)
    saved = []
    for i, image in enumerate(images):
        width, height = image.size
        if width > max_dim or height > max_dim:
            scale_factor = min(max_dim / width, max_dim / height)
            image = image.resize((int(width * scale_factor), int(height * scale_factor)))
        image_path = os.path.join(output_dir, f"page_{i+1}.png")
        image.save(image_path)
        saved.append(image_path)
    return saved


def convert_with_pdftoppm(pdf_path, output_dir, dpi=200) -> List[str]:
    if not shutil.which("pdftoppm"):
        raise FileNotFoundError("pdftoppm not found in PATH")
    prefix = os.path.join(output_dir, "page")
    cmd = ["pdftoppm", "-png", "-r", str(dpi), pdf_path, prefix]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # pdftoppm outputs page-1.png etc.
    return sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith("page") and f.endswith(".png")])


def convert(pdf_path, output_dir, max_dim=1000, dpi=200):
    try:
        return convert_with_pdf2image(pdf_path, output_dir, max_dim=max_dim, dpi=dpi)
    except Exception:
        # Try pdftoppm fallback
        return convert_with_pdftoppm(pdf_path, output_dir, dpi=dpi)


# Tool schema for chat tool-calling
tool = {
    "type": "function",
    "function": {
        "name": "convert_pdf_to_images",
        "description": "Convert a PDF to PNG images and return the saved file paths.",
        "parameters": {
            "type": "object",
            "properties": {
                "pdf_path": {"type": "string", "description": "Absolute path to the PDF file."},
                "output_dir": {"type": "string", "description": "Directory to store PNGs. If omitted, a temp dir is used."},
                "max_dim": {"type": "integer", "description": "Maximum width/height for output images.", "default": 1000},
                "dpi": {"type": "integer", "description": "DPI used when rasterizing the PDF.", "default": 200},
            },
            "required": ["pdf_path"],
        },
    },
}


def handle(pdf_path: str, output_dir: str = None, max_dim: int = 1000, dpi: int = 200):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        paths = convert(pdf_path, output_dir, max_dim=max_dim, dpi=dpi)
        return {"images": paths, "output_dir": output_dir}
    with TemporaryDirectory() as tmpdir:
        paths = convert(pdf_path, tmpdir, max_dim=max_dim, dpi=dpi)
        return {"images": paths, "output_dir": tmpdir}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf_to_images.py [input pdf] [output directory]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_directory = sys.argv[2]
    paths = convert(pdf_path, output_directory)
    print("\n".join(paths))
