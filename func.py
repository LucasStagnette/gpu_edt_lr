import requests
import os
from dotenv import load_dotenv
LOGIN_URL = (
    "https://www.gpu-lr.fr/sat/index.php?"
    "page_param=accueilsatellys.php&cat=0&numpage=1&niv=0&clef=/"
)

load_dotenv()

def connect_and_download(number: str, weeks: list):
    """
    this function connect to gpu and download the week(s) asked of your student number
    """
    sess = requests.Session()

    headers = {
        "Host": "www.gpu-lr.fr",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) "
            "Gecko/20100101 Firefox/143.0"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.gpu-lr.fr",
        "Connection": "keep-alive",
        "Referer": LOGIN_URL,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "DNT": "1",
        "Sec-GPC": "1",
    }

    payload = {
        "modeconnect": "connect",
        "util": number,
        "acct_pass": str(os.getenv("PASSWORD"))
    }

    sess.post(LOGIN_URL, headers=headers, data=payload)
    sess.get("https://www.gpu-lr.fr/gpu/index.php?page_param=fpetudiant.php&cat=0&numpage=1&niv=2&clef=/10192/10194/")
    for week in weeks:
        resp = sess.get(f"https://www.gpu-lr.fr/gpu/gpu2vcs.php?semaine={week}&prof_etu=ETU&etudiant={number}&enseignantedt=")
        with open(f"{number}_vcs/{week}.vcs", "w") as file:
            file.write(resp.text)





connect_and_download("222842", ["41", "40"])