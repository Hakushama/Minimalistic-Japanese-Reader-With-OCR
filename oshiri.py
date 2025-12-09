import tkinter as tk
import pyautogui
import time
import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from tkinter import filedialog
import json
from manga_ocr import MangaOcr
import pyanime4k

import oppai

print_mode : bool = False
was_last_print_successful : bool = False
default_session_config = {
            "config": {"current_session_id" : 1},
            "sessions": {
                1 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                2 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                3 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                4 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                5 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                6 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                7 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                8 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0},
                9 : {"display_text" : "", "invert_mode" : False, "current_image_directory" : "", "image_scale" : 1.0, "image_index" : 0}
        }
        }

def snip_and_save():
    global print_mode
    print_mode = True
    toplevel = tk.Toplevel()
    toplevel.attributes("-fullscreen", True)
    toplevel.attributes("-alpha", 0.2)
    toplevel.configure(bg='green')
    toplevel.title("Snipping Tool")
    toplevel.attributes("-topmost", True)
    toplevel.lift()

    canvas = tk.Canvas(toplevel, cursor="cross", bg="gray")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = end_x = end_y = 0
    rect = None
    snip_done = [False]

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_mouse_move(event):
        if rect:
            canvas.coords(rect, start_x, start_y, event.x, event.y)


    def on_mouse_up(event):
        global was_last_print_successful
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        snip_done[0] = True
        toplevel.destroy()

        if snip_done[0]:
            global print_mode
            left = min(start_x, end_x)
            top = min(start_y, end_y)
            right = max(start_x, end_x)
            bottom = max(start_y, end_y)
            cropped = screenshot.crop((left, top, right, bottom))
            save_path = os.path.join(os.getcwd(), oppai.PATH+"\\temp\\snip.jpg")
            cropped.save(save_path)
            #print(f"Snip saved to {save_path}")
            was_last_print_successful = True
            print_mode = False
            if oppai.ocr_mode == "OcrNew":
                oppai.event_queue.append("OcrNew")
            elif oppai.ocr_mode == "OcrAdd":
                oppai.event_queue.append("OcrAdd")

            return True
        else:
            was_last_print_successful = False
            print_mode = False


    def cancel_snip(event=None):
        global was_last_print_successful
        global print_mode
        #print("Snip canceled.")
        snip_done[0] = False
        print_mode = False
        was_last_print_successful = False
        toplevel.destroy()


    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    canvas.bind("<ButtonPress-3>", cancel_snip)
    toplevel.bind("<Escape>", cancel_snip)

    # Hide the window for the screenshot
    toplevel.update()
    toplevel.withdraw()
    time.sleep(0.1)
    screenshot = pyautogui.screenshot()
    toplevel.deiconify()


def get_white_pixel_percentage(img, white_threshold_min=248, white_threshold_max=255):
    """
    Calculates the percentage of pixels considered 'white' in a grayscale image.

    Args:
        img: PIL Image object (any mode)
        white_threshold_min: Minimum intensity to consider as white (default: 248)
        white_threshold_max: Maximum intensity (usually 255)

    Returns:
        float: Percentage of white pixels (0.0 to 100.0)
    """
    try:
        # Convert to grayscale if not already
        if img.mode != 'L':
            img = img.convert('L')

        # Convert to numpy array
        img_array = np.array(img)

        # Count pixels in the white range [248, 255]
        white_pixels = np.sum((img_array >= white_threshold_min) & (img_array <= white_threshold_max))

        # Total number of pixels
        total_pixels = img_array.size

        if total_pixels == 0:
            return 0.0

        # Calculate percentage
        percentage = (white_pixels / total_pixels) * 100

        return round(percentage, 4)

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def invert_image_colors(image):
    # Invert the colors
    inverted_image = ImageOps.invert(image)
    return inverted_image

def get_image_files(directory):
    # Get all files in directory with image extensions and sort them
    #directory = directory.replace("/", "\\")
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and (".png" in str(f) or ".jpg" in str(f) or ".jpeg" in str(f) or ".webp" in str(f) or ".tiff" in str(f))]
    for i in range(len(files)):
        files[i] = directory+"/"+files[i]

    oppai.images_in_folder_paths = files
    #print(str(files))
    return files


def get_directory():
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        return directory
    else:
        return None

def rescale_image(image : Image, multiplier : float = 1.0):
    processor = pyanime4k.Processor(
        processor_type="cpu",
        device=0,
        model="acnet-hdn0"
    )

    src = np.asarray(image)
    dst = processor(src, factor=multiplier)
    return Image.fromarray(dst)


def rescale_image_old(image : Image, multiplier : float = 1.0):
    width = image.size[0]*multiplier
    height = image.size[1]*multiplier
    return image.resize((round(width), round(height)), Image.Resampling.LANCZOS)

def check_if_config_exists_and_create_one_if_it_does_not():
    if not os.path.isfile(oppai.PATH+"\\config.json"):
        data = default_session_config
        with open(oppai.PATH+"\\config.json", 'w') as file:
            json.dump(data, file, indent=4)

def ocr_with_mangaocr(img):
    mocr = MangaOcr()
    return mocr(img)

