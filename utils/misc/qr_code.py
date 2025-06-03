import qrcode


async def create_qr_code(user_number):
    url = f'https://t.me/Kofelevs_bonuses_bot?start={user_number}'

    return qrcode.make(url)
