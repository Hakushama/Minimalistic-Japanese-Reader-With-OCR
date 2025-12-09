import oshiri
from PIL import Image
import json
import os

PATH = os.path.dirname(__file__)
display_text : str = "おっぱい"
text_orientation = 'vertical'
invert_mode : bool = False
reset_y : bool = False
images_in_folder = []
images_in_folder_inverted = []
images_in_folder_paths = []
event_queue = []
image_scale : float = 1.0
image_index = 0
current_image_directory = ""
current_session_id = 1
ocr_mode = "OcrNew"
high_quality_scaling : bool = False

def ocr_new():
    global ocr_mode
    ocr_mode = "OcrNew"
    oshiri.snip_and_save()


def ocr_new2():
    text = oshiri.ocr_with_mangaocr(PATH+"\\temp\\snip.jpg")
    if text and text != "":
        global display_text
        display_text = text

def ocr_add():
    global ocr_mode
    ocr_mode = "OcrAdd"
    oshiri.snip_and_save()

def ocr_add2():
    global display_text
    display_text += oshiri.ocr_with_mangaocr(PATH+"\\temp\\snip.jpg")

def invert_color_of_text_image(image):
    white_percentage = oshiri.get_white_pixel_percentage(image)
    if white_percentage:
        if white_percentage > 70.0:
            return oshiri.invert_image_colors(image)
        else:
            return image
    else:
        return image

def set_directory():
    directory = oshiri.get_directory()
    if not directory:
        return
    global images_in_folder
    global images_in_folder_inverted
    global current_image_directory
    file_paths = oshiri.get_image_files(directory)
    images_in_folder = []
    for i in file_paths:
        images_in_folder.append(Image.open(i))

    images_in_folder_inverted = []
    for i in images_in_folder:
        images_in_folder_inverted.append(invert_color_of_text_image(i))

    #print("Inverted Images: " + str(images_in_folder_inverted))
    current_image_directory = directory
    event_queue.append("load_image")
    event_queue.append("reset_index")



def load_session():
    with open(PATH+"\\config.json", 'r') as file:
        data = json.load(file)
        global current_session_id
        current_session_id = current_session_id
        stringfied_current_session_id = str(current_session_id)
        #print(stringfied_current_session_id)
        session_data = data["sessions"][stringfied_current_session_id]
        global display_text, invert_mode, current_image_directory, image_scale, image_index, text_orientation
        display_text = session_data["display_text"]
        invert_mode = session_data["invert_mode"]
        current_image_directory = session_data["current_image_directory"]
        image_scale = session_data["image_scale"]
        image_index = session_data["image_index"]
        text_orientation = session_data["text_orientation"]

        if current_image_directory and current_image_directory != "" and os.path.isdir(current_image_directory):
            file_paths = oshiri.get_image_files(current_image_directory)

            global images_in_folder
            images_in_folder = []

            for i in file_paths:
                images_in_folder.append(Image.open(i))

            global images_in_folder_inverted
            images_in_folder_inverted = []

            for i in images_in_folder:
                images_in_folder_inverted.append(invert_color_of_text_image(i))
            #print("Inverted Images: " + str(images_in_folder_inverted))
            event_queue.append("load_image")

def save_session():
    with open(PATH+"\\config.json", 'r') as file:
        data = json.load(file)
        global display_text, invert_mode, current_image_directory, image_scale, image_index, current_session_id
        data["config"]["current_session_id"] = current_session_id
        data["sessions"][str(current_session_id)]["display_text"] = display_text
        data["sessions"][str(current_session_id)]["invert_mode"] = invert_mode
        data["sessions"][str(current_session_id)]["current_image_directory"] = current_image_directory
        data["sessions"][str(current_session_id)]["image_scale"] = image_scale
        data["sessions"][str(current_session_id)]["image_index"] = image_index
        data["sessions"][str(current_session_id)]["text_orientation"] = text_orientation
        with open(PATH+"\\config.json", 'w') as writer:
            json.dump(data, writer, indent=4, ensure_ascii=False)












