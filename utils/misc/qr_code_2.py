import qrcode
from qrcode.image.styledpil import StyledPilImage

qr = qrcode.QRCode(version=2,
error_correction=qrcode.constants.ERROR_CORRECT_L,
box_size=10, border=4)
qr.add_data('https://t.me/Kofelevs_IE_bot?start=5669831950M')


img_3 = qr.make_image(embeded_image_path="python.png")

img_3.save("qrcode5.png")