import csv

from PIL import Image, ImageDraw, ImageFont
import textwrap

# For barcode
from io import BytesIO
from barcode import Code128
from barcode.writer import ImageWriter
import PySimpleGUI as sg
import os

# For Program logic
# Template Dimension
MAX_W, MAX_H = 428, 926

# For GUI
BUTTON_SIZE = 8

home_dir = os.path.expanduser('~')
download_dir = os.path.join(home_dir, 'Downloads')

icon_path = 'barcode_pencil.ico'

sg.theme('DarkBlue17')

sg.set_global_icon(icon_path)

SETTINGS_PATH = os.path.curdir
settings = sg.UserSettings(path=SETTINGS_PATH , filename='config.ini', use_config_file=True, convert_bools_and_none=True)

description_font_size = int(settings["VOUCHER"]["description_font_size"])
title_font_size = int(settings["VOUCHER"]["title_font_size"])
description_break = int(settings["VOUCHER"]["description_break"])
save_folder_name = str(settings["VOUCHER"]["save_folder_name"])

layout = [
            [sg.StatusBar("Voucher Barcode Generator", justification='c', font=(None, 22), pad=(0, 10) , key='-STATUSBAR-')],
            [sg.Text("csv file:", size=(12, 1), justification='r', tooltip='The csv file should have 3 values: Merchant name, Description, Voucher code'), sg.Input(key="-CSVFILE-", expand_x=True), sg.FileBrowse(file_types=(('csv files', '*.csv'), ), size=BUTTON_SIZE, initial_folder=home_dir)],
            [sg.Text("Destination:", size=(12, 1), justification='r', tooltip="The location where generated files are going to be saved"), sg.Input(key='-DESTINATIONDIR-', expand_x=True), sg.FolderBrowse(size=BUTTON_SIZE, initial_folder=home_dir)],
            [sg.HorizontalSeparator(pad=(0, 10))],
            [sg.Push(), sg.ProgressBar(max_value = 100, orientation='h', size=(55, 15), border_width=2, pad=((0, 0), (10, 20)), bar_color=('Green', None) , key='-PROGBAR-'), sg.Push()],
            [sg.Button("Settings", size=BUTTON_SIZE), sg.Push(), sg.Ok(button_text="Generate", size=BUTTON_SIZE), sg.Exit(button_color='tomato', size=BUTTON_SIZE)],
]

window = sg.Window('Voucher Barcode Generator', layout, font=(None, 10))

def is_valid_path(filepath):
    if filepath and os.path.exists(filepath):
        return True
    sg.popup('Filepath not correct', title="Error")
    return False


def write_description(desc, draw_obj):
    para = textwrap.wrap(desc, width=description_break)
    font = ImageFont.truetype('Roboto-Regular.ttf', description_font_size)

    current_h, pad = 100, 10
    for line in para:
        w, h = draw_obj.textsize(line, font=font)
        draw_obj.text(((MAX_W - w) / 2, current_h), line, font=font, fill =(0, 0, 0))
        current_h += h + pad


def write_title(curr_title, draw_obj):
    font_title = ImageFont.truetype('Roboto-Bold.ttf', title_font_size)
    title_h = 20

    w, h = draw_obj.textsize(curr_title, font=font_title)
    draw_obj.text(((MAX_W - w) / 2, title_h), curr_title, font=font_title, fill=(0, 0, 0))


def appned_barcode(base_img, code_str):
    raw_fp = BytesIO()

    generated_barcode = Code128(code_str, writer=ImageWriter())
    generated_barcode.write(raw_fp)

    barcode_ = Image.open(raw_fp)
    barcode_ = barcode_.resize((428, 170))

    base_img.paste(barcode_, (0, 200))

def get_counts(file):
    with open(file) as f: return len(f.readlines())

def generate_output(csv_file, destination):
    with open(csv_file, 'r') as f:
        data = csv.reader(f)
        total_rows = get_counts(csv_file)
        count = 0

        if total_rows == 0: return "empty"
        progress_val = 0
        progress_sum = 100 / total_rows
        for row in data:
            count += 1
            try:
                title, description, code = row
            except ValueError as ve:
                sg.popup_auto_close(f'{ve} (Line-{count})', title="Error", auto_close_duration=2)
                continue
            #
            event, values = window.read(timeout=1)
            progress_val += progress_sum
            window['-PROGBAR-'].update_bar(progress_val)
            #
            # cleaning whitespaces
            title = title.strip()
            code = code.strip()
            description = description.strip()

            im = Image.open('Template.png')
            draw = ImageDraw.Draw(im)

            write_title(title, draw_obj=draw)
            write_description(desc=description, draw_obj=draw)

            appned_barcode(base_img=im, code_str=code)
            root_name = str(count) + "-" + title
            filename = ".".join((root_name, 'png'))
            
            save_path = os.path.join(destination, save_folder_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            save_filename = os.path.join(save_path, filename)
            im.save(save_filename)
        sg.popup_quick_message('Completed', relative_location=(0, 120))


def settings_window(settings):
    layout = [
            [sg.Text("SETTINGS", pad=((0, 0), (10, 20)))],
            [sg.Text('Font size for Voucher name', size=25, justification='r'), sg.Input(settings["VOUCHER"]["title_font_size"], size=2, key='-TITLE_FONT_SIZE-')],
            [sg.Text('Font size for Description', size=25, justification='r'), sg.Input(settings["VOUCHER"]["description_font_size"], size=2, key='-DESC_FONT_SIZE-'),],
            [sg.Text('Breakpoint occur at', size=25, justification='r'), sg.Input(settings["VOUCHER"]["description_break"], size=2, key='-DESC_BREAK-')],
            [sg.Text('Default folder name', size=25, justification='r'), sg.Input(settings["VOUCHER"]["save_folder_name"], size=20, key='-FOLDER_NAME-')],
            [sg.HorizontalSeparator(pad=(0, 10))],
            [sg.Push(), sg.Button("Restore Defaults", size=16), sg.Button("Save Settings", size=16), sg.Push()]
    ]

    window = sg.Window("Settings", layout=layout, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Save Settings":
            settings["VOUCHER"]["title_font_size"] = values['-TITLE_FONT_SIZE-']
            settings["VOUCHER"]["description_font_size"] = values['-DESC_FONT_SIZE-']
            settings["VOUCHER"]["description_break"] = values['-DESC_BREAK-']
            settings["VOUCHER"]["save_folder_name"] = values['-FOLDER_NAME-']

            global description_font_size
            global title_font_size
            global description_break
            global save_folder_name

            description_font_size = int(settings["VOUCHER"]["description_font_size"])
            title_font_size = int(settings["VOUCHER"]["title_font_size"])
            description_break = int(settings["VOUCHER"]["description_break"])
            save_folder_name = str(settings["VOUCHER"]["save_folder_name"])

            sg.popup_no_titlebar("Settings saved!")
            break
        elif event == "Restore Defaults":
            window['-TITLE_FONT_SIZE-'].update(value=20)
            window['-DESC_FONT_SIZE-'].update(value=22)
            window['-DESC_BREAK-'].update(value=35)
            window['-FOLDER_NAME-'].update(value='batch-generated')
    window.close()

while True:
    event, values = window.read()
    # debugging
    print(f'Event name: {event}')
    print('------')
    for k, v in values.items():
        print(f'{k}: {v}')

    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    if not values['-CSVFILE-'] and event == 'Generate':
        sg.popup_ok("Please select a csv file", title="Error")
    elif not values['-DESTINATIONDIR-'] and event == 'Generate':
        if sg.popup_yes_no("Do you want to save the result in Downloads folder?", title="Confirmation") == 'Yes':
            window['-DESTINATIONDIR-'].update(value=download_dir)
    elif event == 'Generate':
        if is_valid_path(values['-CSVFILE-']) and is_valid_path(values['-DESTINATIONDIR-']):
            if generate_output(csv_file=values['-CSVFILE-'], destination=values['-DESTINATIONDIR-']) == 'empty':
                sg.popup('csv file is empty', title='Error')

    elif event == "Settings":
        settings_window(settings=settings)
window.close()
