import requests

LOGIN = "redcorner21@mail.ru"
PASSWORD = "hhnbmc"


# Получаем токен
token_resp = requests.get(
    "https://api.vendista.ru:99/token",
    params={"login": LOGIN, "password": PASSWORD}
)
token = token_resp.json()["token"]
print(token)