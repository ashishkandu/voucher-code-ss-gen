import csv

from PIL import Image, ImageDraw, ImageFont
import textwrap

from os.path import join

# For barcode
from io import BytesIO
from barcode import Code128
from barcode.writer import ImageWriter

# title = 'TGV Cinemas'
# description = 'RM16.70 for e-Voucher Movie Ticket worth up to RM23.'
# code = 'HOT1500020062238'


MAX_W, MAX_H = 428, 926

description_font_size = 20
title_font_size = 22
description_break = 35


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

    # base_img.paste(barcode_, (-15, 200))
    base_img.paste(barcode_, (0, 200))


with open('data.csv', 'r') as f:
    data = csv.reader(f)
    count = 0
    for row in data:
        count += 1
        title, description, code = row
        
        title = title.strip()
        code = code.strip()
        description = description.strip()

        im = Image.open('Template.png')
        draw = ImageDraw.Draw(im)

        write_title(title, draw_obj=draw)
        write_description(desc=description, draw_obj=draw)

        appned_barcode(base_img=im, code_str=code)
        root_name = title + "-" + str(count)
        filename = ".".join((root_name, 'png'))
        save_path = join('batch-generation', filename)
        im.save(save_path)