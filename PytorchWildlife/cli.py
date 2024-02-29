import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Final, List, Tuple

import cv2
import numpy as np
import torchvision
import torchvision.transforms as transforms
from colorama import Fore
from colorama import init as colorama_init
from numpy import ndarray
from torch import Tensor
from tqdm import tqdm

from PytorchWildlife.models import detection as pw_detection


colorama_init(autoreset=True)


IMAGE_SHAPE_FOR_DETECTION: Final[Tuple[int, int]] = (1280, 1280)
ANIMALS_SUBFOLDER: Final[str] = "animals"
NO_ANIMALS_SUBFOLDER: Final[str] = "no_animals"


model = None


def detect_animals(image: Tensor) -> Any:
    global model
    if model is None:
        model = pw_detection.MegaDetectorV5()  # Model weights are automatically downloaded.
    image = image.clone().detach()
    image = transforms.Resize(IMAGE_SHAPE_FOR_DETECTION)(image)
    norm_image = image.float() / image.max()
    out = model.single_image_detection(norm_image)  # TODO Batch detection?
    return out["detections"]


def read_image(image_path: Path) -> Tensor:
    image = torchvision.io.read_image(str(image_path))
    chns, rows, cols = image.shape
    if chns == 4:
        # The detection model doesn't support alpha channels
        image = image[:3]
    return image


def sanity_check_folder(image_paths: List[Path]) -> None:
    for image_path in tqdm(image_paths):
        try:
            assert image_path.is_file()
            torchvision.io.read_image(str(image_path))
        except Exception:
            print(Fore.RED + f"`{image_path}` is not a valid image file. Please remove `{image_path}` and try again.")
            sys.exit(0)


def sort_images(folder: Path) -> None:
    image_paths = list(folder.iterdir())
    sanity_check_folder(image_paths)

    for subfolder in [ANIMALS_SUBFOLDER, NO_ANIMALS_SUBFOLDER]:
        (folder / subfolder).mkdir()

    for image_path in tqdm(image_paths):
        image = read_image(image_path)
        det_result = detect_animals(image)
        contains_animal = len(det_result) != 0
        new_folder = folder / (ANIMALS_SUBFOLDER if contains_animal else NO_ANIMALS_SUBFOLDER)
        shutil.move(image_path, new_folder)


def display_animals(folder: Path, trace_color: Tuple[int, int, int] = (0, 0, 255), trace_size: int = 10):
    for image_path in tqdm(list(folder.iterdir())):
        image = read_image(image_path)
        original_chns, original_rows, original_cols = image.shape
        original_image = np.array(image.clone().detach().permute(1, 2, 0))

        detections = detect_animals(image)
        if len(detections) == 0:
            continue  # Don't display an image without animals

        for detection in detections:
            xyxy, *_ = detection
            x0, y0, x1, y1 = [
                int(v * (original_cols if i % 2 == 0 else original_rows) / IMAGE_SHAPE_FOR_DETECTION[i % 2])
                for i, v in enumerate(xyxy)
            ]
            cv2.rectangle(original_image, (x0, y0), (x1, y1), trace_color, trace_size)

        display_image(original_image)


def display_image(image: ndarray, window_name: str = "image") -> None:
    # Without downsampling, the image can take up too much screen space
    cv2.imshow(window_name, np.array(image)[::4, ::4])
    while True:
        any_key_is_pressed = cv2.waitKey(1) > 0
        window_is_closed = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1
        if any_key_is_pressed or window_is_closed:
            break
    cv2.destroyAllWindows()


def process_images(args: argparse.Namespace) -> None:
    if args.mode == "sort":
        sort_images(Path(args.folder))
    else:
        display_animals(Path(args.folder))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A CLI for finding animals in images.")
    parser.add_argument("folder", type=str, help="folder with images")
    parser.add_argument(
        "--mode", default="display", choices=["sort", "display"], help="display (default) or sort images with animals"
    )
    return parser.parse_args()


def main():
    process_images(parse_args())


if __name__ == "__main__":
    main()
