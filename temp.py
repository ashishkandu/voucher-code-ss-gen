from barcode import EAN13
from barcode.writer import ImageWriter

bar_code = 310400070000555
bar_code = str(bar_code)
bar_code_obj = EAN13(bar_code, writer=ImageWriter())
bar_code_obj.save("bar_code_img")