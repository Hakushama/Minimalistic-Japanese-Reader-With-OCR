import tkinter as tk
import time

from PIL import ImageTk

import oshiri
import pyperclip
import webbrowser
import json

import oppai

event_queue = []

hotkey_cooldown = 0

# Tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() - 96
        y += self.widget.winfo_rooty() + 40
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip.geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="black", fg="gray", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class DraggableWidget:
    def __init__(self, widget):
        self.widget = widget
        self.x = 0
        self.y = 0
        # Bind mouse events
        self.widget.bind("<Button-1>", self.start_drag)
        self.widget.bind("<B1-Motion>", self.on_drag)

    def start_drag(self, event):
        # Store initial mouse position relative to widget
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        # Calculate new position
        new_x = event.x_root - self.x - self.widget.winfo_rootx() + self.widget.winfo_x()
        new_y = event.y_root - self.y - self.widget.winfo_rooty() + self.widget.winfo_y()
        # Move widget to new position
        self.widget.place(x=new_x, y=new_y)

def make_draggable(widget, root):
    def start_move(event):
        widget.x = event.x
        widget.y = event.y

    def do_move(event):
        x = root.winfo_pointerx() - widget.x
        y = root.winfo_pointery() - widget.y
        root.geometry(f"+{x}+{y}")

    widget.bind("<Button-1>", start_move)
    widget.bind("<B1-Motion>", do_move)

def main():
    oshiri.check_if_config_exists_and_create_one_if_it_does_not()

    with open(oppai.PATH+"\\config.json", 'r') as file:
        data = json.load(file)
        oppai.current_session_id = int(data["config"]["current_session_id"])


    root = tk.Tk()
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)
    root.geometry("640x640")
    root.iconbitmap(oppai.PATH+"\\ICON.ico")


    def tog_fullscreen(event):
        if root.focus_get() is not None and root.state() == "normal" and not root.attributes("-fullscreen"):
            root.attributes("-fullscreen", True)
        elif root.focus_get() is not None and root.state() == "normal" and root.attributes("-fullscreen"):
            root.attributes("-fullscreen", False)

    root.bind("<Alt-Return>", tog_fullscreen)

    title_bar = tk.Frame(root, bg="#1E1F22", relief="raised", bd=0, width=372)
    title_bar.pack_propagate(False)
    title_bar.pack(side="right", fill=tk.Y)

    title_bar_bd = tk.Frame(root, bg="gray", relief="raised", bd=0, width=1)
    title_bar_bd.pack_propagate(False)
    title_bar_bd.pack(side="right", fill=tk.Y)

    make_draggable(title_bar, root)

    title_bar_control_buttons = tk.Frame(title_bar, bg="#16171A", relief="raised", bd=0, height=38)
    title_bar_control_buttons.pack_propagate(False)
    title_bar_control_buttons.pack(side="top", fill=tk.X)

    exit_btn = tk.Button(title_bar_control_buttons, text="X", command=root.destroy, bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 12, "bold"),padx=10)
    exit_btn.pack(side=tk.RIGHT, anchor="ne")
    ToolTip(exit_btn, "Exit the program")

    minimize_btn = tk.Button(title_bar_control_buttons, text="-", command=lambda: event_queue.append("minimize"), bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 12, "bold"),padx=10)
    minimize_btn.pack(side=tk.RIGHT, anchor="ne")
    ToolTip(minimize_btn, "Minimize the program")

    # Content
    content = tk.Frame(root, bg="#16171A")
    def pick_directory():
        oppai.set_directory()


    pick_dir = tk.Button(title_bar, text="Select Directory", command=lambda: pick_directory(),
                                  bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444",
                                  activeforeground="#ffffff", borderwidth=3, relief="raised",
                                  font=("Helvetica", 14, "bold"), padx=2, pady=4)
    pick_dir.pack(side=tk.TOP, pady=10)
    ToolTip(pick_dir, "Pick the folder to load...")

    display_page_count_and_index = tk.Label(title_bar, text="0/0", font=("Helvetica", 18, "bold"), bg="#1E1F22",
                      fg="gray")
    display_page_count_and_index.pack(anchor="center")

    content.pack(expand=True, fill=tk.BOTH)

    #Image Operations
    img_label = tk.Label(content, bg="#16171A")

    def on_arrow_next(event):
        global hotkey_cooldown
        if hotkey_cooldown > time.time()*1000:
            return
        hotkey_cooldown = time.time()*1000+50

        oppai.image_index += 1
        if oppai.image_index >= len(oppai.images_in_folder):
            oppai.image_index = 0

        img = oppai.images_in_folder[oppai.image_index]
        if oppai.invert_mode:
            img = oppai.images_in_folder_inverted[oppai.image_index]

        if oppai.reset_y:
            img_label.place(x=img_label.winfo_x(), y=0)

        if not img:
            event_queue.append("load_image")
            return

        if oppai.image_scale != 1.0:
            img = oshiri.rescale_image(img, oppai.image_scale)

        if not img:
            event_queue.append("load_image")
            return



        photo = ImageTk.PhotoImage(img)
        img_label.configure(image=photo)
        img_label.image = photo


    root.bind("<KeyPress-Right>", on_arrow_next)
    root.bind("<KeyPress-d>", on_arrow_next)

    def on_arrow_previous(event):
        global hotkey_cooldown
        if hotkey_cooldown > time.time() * 1000:
            return
        hotkey_cooldown = time.time() * 1000 + 50

        oppai.image_index -= 1
        if oppai.image_index < 0:
            oppai.image_index = len(oppai.images_in_folder)-1

        img = oppai.images_in_folder[oppai.image_index]
        if oppai.invert_mode:
            img = oppai.images_in_folder_inverted[oppai.image_index]

        if oppai.reset_y:
            img_label.place(x=img_label.winfo_x(), y=0)

        if not img:
            event_queue.append("load_image")
            return

        if oppai.image_scale != 1.0:
            img = oshiri.rescale_image(img, oppai.image_scale)

        if not img:
            event_queue.append("load_image")
            return

        photo = ImageTk.PhotoImage(img)
        img_label.configure(image=photo)
        img_label.image = photo

    root.bind("<KeyPress-Left>", on_arrow_previous)
    root.bind("<KeyPress-d>", on_arrow_previous)

    img_label.propagate(False)
    img_label.place(x=0, y=0)

    def on_scroll(event):
        # Adjust y-position based on scroll direction
        value = 0
        if event.delta > 0:
            value = 100
        elif event.delta < 0:
            value = -100

        # Update label position
        img_label.place(x=img_label.winfo_x(), y=img_label.winfo_y()+value)

    root.bind("<MouseWheel>", on_scroll)


    def on_zoom_in(event):
        global hotkey_cooldown
        if hotkey_cooldown > time.time() * 1000:
            return
        hotkey_cooldown = time.time() * 1000 + 50

        img = oppai.images_in_folder[oppai.image_index]
        if oppai.invert_mode:
            img = oppai.images_in_folder_inverted[oppai.image_index]

        if not img:
            event_queue.append("load_image")
            return

        if img_label.cget("image"):
            oppai.image_scale += .1
            if oppai.image_scale != 1.0:
                img = oshiri.rescale_image(img, oppai.image_scale)

            if not img:
                event_queue.append("load_image")
                return

            photo = ImageTk.PhotoImage(img)
            img_label.configure(image=photo)
            img_label.image = photo


    def move_image_up(event):
        img_label.place(x=img_label.winfo_x(), y=img_label.winfo_y() + 150)

    root.bind("<KeyPress-Up>", move_image_up)
    root.bind("<KeyPress-w>", move_image_up)
    root.bind("<KeyPress-plus>", on_zoom_in)
    root.bind("<KeyPress-e>", on_zoom_in)

    def on_zoom_out(event):
        global hotkey_cooldown
        if hotkey_cooldown > time.time() * 1000:
            return
        hotkey_cooldown = time.time() * 1000 + 50

        img = oppai.images_in_folder[oppai.image_index]
        if oppai.invert_mode:
            img = oppai.images_in_folder_inverted[oppai.image_index]

        if not img:
            event_queue.append("load_image")
            return

        if img_label.cget("image"):
            oppai.image_scale -= .1
            if oppai.image_scale != 1.0:
                img = oshiri.rescale_image(img, oppai.image_scale)

            if not img:
                event_queue.append("load_image")
                return

            photo = ImageTk.PhotoImage(img)
            img_label.configure(image=photo)
            img_label.image = photo

    def move_image_down(event):
        img_label.place(x=img_label.winfo_x(), y=img_label.winfo_y() - 150)

    root.bind("<KeyPress-Down>", move_image_down)
    root.bind("<KeyPress-s>", move_image_down)
    root.bind("<KeyPress-minus>", on_zoom_out)
    root.bind("<KeyPress-q>", on_zoom_out)

    draggable_label = DraggableWidget(img_label)

    text_box = tk.Frame(title_bar, bg="#16171A", relief="raised", bd=0, height=192, width=348)
    text_box.pack_propagate(False)
    text_box.pack(anchor="center", pady=20)


    def on_text_enter(event):
        text.config(state="normal")

    def on_text_leave(event):
        text.config(state="disabled")
        pass

    text = tk.Text(text_box, height=192, width=348, wrap="word", font=("MS Gothic", 14), bg="black", fg="white")
    text.pack(side=tk.LEFT)
    text.bind("<Enter>", on_text_enter)
    text.bind("<Leave>", on_text_leave)

    scrollbar = tk.Scrollbar(text_box, orient=tk.VERTICAL, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scrollbar.set)



    ocr_buttons = tk.Frame(title_bar, bg="#1E1F22", relief="raised", bd=0, height=48)
    ocr_buttons.pack_propagate(False)
    ocr_buttons.pack(anchor="center", fill=tk.X)

    btn_ocr_text_copy = tk.Button(ocr_buttons, text="Copy", command=lambda: pyperclip.copy(oppai.display_text), bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 14, "bold"),padx=2)
    btn_ocr_text_copy.place(x=8, y=0)
    ToolTip(btn_ocr_text_copy, "Copy all text to clipboard.")

    btn_open_in_jisho = tk.Button(ocr_buttons, text="Jisho", command=lambda: webbrowser.open("https://jisho.org/search/"+oppai.display_text), bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 14, "bold"),padx=2)
    btn_open_in_jisho.place(x=80, y=0)
    ToolTip(btn_open_in_jisho, "Tries to open the Jisho page for the\ndisplayed text, only works for single words.")

    btn_ocr_new = tk.Button(ocr_buttons, text="OCR New", command=lambda: event_queue.append("OcrNew"), bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 14, "bold"),padx=2)
    btn_ocr_new.place(x=154, y=0)
    ToolTip(btn_ocr_new, "Click to use the ocr tool, this mode \nwill replace the current text in the box.")

    btn_ocr_add = tk.Button(ocr_buttons, text="OCR Add", command=lambda: event_queue.append("OcrAdd"), bg="#2b2b2b", fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3, relief="raised",font=("Helvetica", 14, "bold"),padx=2)
    btn_ocr_add.place(x=263, y=0)
    ToolTip(btn_ocr_add, "Click to use the ocr tool, this mode \nwill add to the current text in the box.")

    def toggle_invert_mode():
        oppai.invert_mode = not oppai.invert_mode
        event_queue.append("load_image")


    def toggle_reset_y_mode():
        oppai.reset_y = not oppai.reset_y

    invert_and_reset_y = tk.Frame(title_bar, bg="#1E1F22", relief="raised", bd=0, height=48, width=226)
    invert_and_reset_y.pack_propagate(False)
    invert_and_reset_y.pack(anchor="center", pady=4)

    btn_tog_invert_mode = tk.Button(invert_and_reset_y, text="Invert Mode", command=lambda: toggle_invert_mode(), bg="#2b2b2b",
                            fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff", borderwidth=3,
                            relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    btn_tog_invert_mode.pack(side="left")
    ToolTip(btn_tog_invert_mode, "Toggles invert mode, if on, images\nwith only text will be inverted.")

    btn_reset_y_on_page_change = tk.Button(invert_and_reset_y, text="Reset Y", command=lambda: toggle_reset_y_mode(), bg="#2b2b2b",
                                    fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff",
                                    borderwidth=3,
                                    relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    btn_reset_y_on_page_change.pack(side="right")
    ToolTip(btn_reset_y_on_page_change, "The Y position will reset on page change.")

    session_shit_frame = tk.Frame(title_bar, bg="#1E1F22", relief="raised", bd=0, height=164)
    session_shit_frame.pack_propagate(False)
    session_shit_frame.pack(fill=tk.X)


    label2 = tk.Label(session_shit_frame, text="Cool session crap", font=("Helvetica", 14, "bold"), bg="#1E1F22", fg="gray")
    label2.place(x=92, y=24)

    current_session_display = tk.Label(session_shit_frame, text=str(oppai.current_session_id), font=("Arial", 28, "bold"), bg="#1E1F22", fg="gray")
    current_session_display.place(x=160, y=60)

    def session_increment():
        oppai.current_session_id+=1
        if oppai.current_session_id > 9:
            oppai.current_session_id = 1
        current_session_display.configure(text=str(oppai.current_session_id))


    session_increment_btn = tk.Button(session_shit_frame, text=">", command=lambda: session_increment(), bg="#2b2b2b",
                                    fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff",
                                    borderwidth=3,
                                    relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    session_increment_btn.place(x=196, y=64)
    ToolTip(session_increment_btn, "Increments session id, you can have\nup to 9 sessions saved.")


    def session_decrement():
        oppai.current_session_id -= 1
        if oppai.current_session_id < 1:
            oppai.current_session_id = 9
        current_session_display.configure(text=str(oppai.current_session_id))



    session_decrement_btn = tk.Button(session_shit_frame, text="<", command=lambda: session_decrement(), bg="#2b2b2b",
                                  fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff",
                                  borderwidth=3,
                                  relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    session_decrement_btn.place(x=124, y=64)
    ToolTip(session_decrement_btn, "Decrements session id, you can have\nup to 9 sessions saved.")

    save = tk.Button(session_shit_frame, text="Save", command=lambda: oppai.save_session(), bg="#2b2b2b",
                                  fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff",
                                  borderwidth=3,
                                  relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    save.place(x=104, y=124)
    ToolTip(save, "Save session.")


    load = tk.Button(session_shit_frame, text="Load", command=lambda: oppai.load_session(), bg="#2b2b2b",
                                  fg="#cccccc", bd=0, activebackground="#444444", activeforeground="#ffffff",
                                  borderwidth=3,
                                  relief="raised", font=("Helvetica", 14, "bold"), padx=2)
    load.place(x=180, y=124)
    ToolTip(load, "Load session.")




    def update():
        if oppai.invert_mode and btn_tog_invert_mode.cget("relief") != "sunken":
            btn_tog_invert_mode.configure(relief="sunken")
        elif not oppai.invert_mode and btn_tog_invert_mode.cget("relief") != "raised":
            btn_tog_invert_mode.configure(relief="raised")

        if oppai.reset_y and btn_reset_y_on_page_change.cget("relief") != "sunken":
            btn_reset_y_on_page_change.configure(relief="sunken")
        elif not oppai.reset_y and btn_reset_y_on_page_change.cget("relief") != "raised":
            btn_reset_y_on_page_change.configure(relief="raised")

        number_to_display = len(oppai.images_in_folder)-1
        if number_to_display == -1:
            number_to_display = 0
        display_page_count_and_index.configure(text=str(oppai.image_index)+"/"+str(number_to_display))

        if text.get("1.0", tk.END).replace("\n", "") != oppai.display_text.replace("\n", ""):
            text.config(state="normal")
            text.delete("1.0", tk.END)
            text.insert("1.0", oppai.display_text)

        if int(current_session_display.cget("text")) != oppai.current_session_id:
            current_session_display.configure(text=str(oppai.current_session_id))

        if event_queue and not oshiri.print_mode:
            event = event_queue.pop()

            if event == "reload_session":
                oppai.load_session()

            if event == "load_image":
                img = oppai.images_in_folder[oppai.image_index]
                if oppai.invert_mode:
                    img = oppai.images_in_folder_inverted[oppai.image_index]

                if oppai.image_scale != 1.0:
                    img = oshiri.rescale_image(img, oppai.image_scale)

                if not img:
                    event_queue.append("load_image")
                    return

                photo = ImageTk.PhotoImage(img)
                img_label.configure(image=photo)
                img_label.image = photo


            if event == "OcrNew":
                oppai.ocr_new()

            if event == "OcrAdd":
                oppai.ocr_add()

            if event == "minimize":
                root.overrideredirect(False)
                root.iconify()



        if oppai.event_queue and not oshiri.print_mode:
            event = oppai.event_queue.pop()

            if event == "OcrNew":
                oppai.ocr_new2()


            if event == "OcrAdd":
                oppai.ocr_add2()

            if event == "reset_index":
                oppai.image_index = 0

            if event == "load_image":
                img = oppai.images_in_folder[oppai.image_index]
                if oppai.invert_mode:
                    img = oppai.images_in_folder_inverted[oppai.image_index]

                if oppai.image_scale != 1.0:
                    img = oshiri.rescale_image(img, oppai.image_scale)
                photo = ImageTk.PhotoImage(img)
                img_label.configure(image=photo)
                img_label.image = photo





        root.after(20, update)

    root.after(20, update)

    root.mainloop()


if __name__ == "__main__":
    main()
