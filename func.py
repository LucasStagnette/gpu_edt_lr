import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
LOGIN_URL = (
    "https://www.gpu-lr.fr/sat/index.php?"
    "page_param=accueilsatellys.php&cat=0&numpage=1&niv=0&clef=/"
)

load_dotenv()

def detect_weeks(number:str):
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
        "util": f"{number}",
        "acct_pass": str(os.getenv("PASSWORD"))
    }

    sess.post(LOGIN_URL, headers=headers, data=payload)
        
    url = "https://www.gpu-lr.fr/gpu/index.php?page_param=fpetudiant.php&cat=0&numpage=1&niv=2&clef=/10192/10194/"
    resp = sess.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    buttons = soup.find_all("button", attrs={"name": lambda x: x and x.startswith("btn_sem_")})
    
    weeks_available = []
    for btn in buttons:
        semaine = btn.get("value")
        etat = "désactivé" if btn.has_attr("disabled") else "cliquable"
        if etat == "cliquable":
            weeks_available.append(str(semaine))
    sess.close()
    return weeks_available



def clean(number:str):
    try:
        os.remove(f"ics_files/{number}.ics")
    except:
        pass

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
        resp.encoding = "utf-8"
        with open(f"{number}_vcs/{week}.vcs", "w") as file:
            file.write(resp.text)

def assemble(number:str, weeks:list):
    with open(f"ics_files/{number}.ics", "w", encoding="utf-8") as f:
        pass
    with open(f"ics_files/{number}.ics", "a", encoding="utf-8") as file:
        file.write("BEGIN:VCALENDAR\nPRODID: Gpu2vcs modified by Dynamisoft\nVERSION:2.0\nMETHOD:PUBLISH")
    for week in weeks:
        with open(f"{number}_vcs/{week}.vcs", "r", encoding="utf-8") as file:
            with open(f"ics_files/{number}.ics", "a", encoding="utf-8") as file2:
                a = file.readlines()[7:-1]
                for line in a:
                    file2.write(line)
    with open(f"ics_files/{number}.ics", "a", encoding="utf-8") as file:
        file.write("END:VCALENDAR\n")

def clean2(number: str, weeks:list):
    for week in weeks:
        os.remove(f"{number}_vcs/{week}.vcs")

