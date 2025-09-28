import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import chardet

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
    this function connect to gpu and download the week(s) asked with your student number
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
    os.mkdir(f"{number}_vcs")
    for week in weeks:
        resp = sess.get(f"https://www.gpu-lr.fr/gpu/gpu2vcs.php?semaine={week}&prof_etu=ETU&etudiant={number}&enseignantedt=")
        
        with open(f"{number}_vcs/{week}.vcs", "w", encoding="utf-8") as file:
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
    os.rmdir(f"{number}_vcs")

import shutil
import re
import quopri
import html

def normalize_ics_to_utf8(path: str) -> str:


    """
    Force un fichier .ics à être encodé en UTF-8 en :
      - détectant et décodant le quoted-printable si présent,
      - ou en détectant l'encodage avec chardet,
      - en décodant puis en re-écrivant en utf-8.
    Retourne l'encodage utilisé/détecté.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    # lire brut
    with open(path, "rb") as f:
        raw = f.read()

    # diagnostic rapide : afficher quelques bytes (hex/text)
    preview = raw[:200]

    # heuristique : présence explicite d'un paramètre ENCODING=QUOTED-PRINTABLE
    is_qp_param = b"ENCODING=QUOTED-PRINTABLE" in raw.upper()
    # heuristique alternative : beaucoup de séquences =XX
    has_eq_hex = bool(re.search(rb'=[0-9A-Fa-f]{2}', raw))

    used_encoding = None
    decoded_bytes = None

    if is_qp_param or has_eq_hex:
        decoded_bytes = quopri.decodestring(raw)
        # tenter plusieurs décodages pour obtenir du texte lisible
        for enc_try in ("utf-8", "utf-8-sig", "cp1252", "iso-8859-1"):
            try:
                text = decoded_bytes.decode(enc_try)
                used_encoding = f"quoted-printable -> {enc_try}"
                break
            except UnicodeDecodeError:
                continue
        else:
            # dernier recours : décoder en utf-8 en remplaçant
            text = decoded_bytes.decode("utf-8", errors="replace")
            used_encoding = "quoted-printable -> utf-8 (replace)"
    else:
        # pas de quoted-printable évident : on essaie chardet puis fallbacks
        guess = chardet.detect(raw)
        enc_guess = guess.get("encoding")
        conf = guess.get("confidence", 0)
        tried = []
        if enc_guess:
            tried.append(enc_guess)
        tried.extend(["utf-8", "cp1252", "iso-8859-1"])
        for enc_try in tried:
            try:
                text = raw.decode(enc_try)
                used_encoding = enc_try
                break
            except Exception:
                continue
        else:
            text = raw.decode("utf-8", errors="replace")
            used_encoding = "utf-8 (replace)"

    # décoder les entités HTML si présentes (&eacute; etc.)
    text2 = html.unescape(text)

    # Optionnel : normaliser les retours chariot (ics veut CRLF mais UTF-8 text ok)
    # text2 = text2.replace("\r\n", "\n").replace("\r", "\n")

    # écrire proprement en UTF-8
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text2)
    return used_encoding

def reformat(number: str):

    path = f"ics_files/{number}.ics"

    new_lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("SUMMARY:"):
                content = line[len("SUMMARY:"):].strip()
                parts = content.split(" / ")
                if len(parts) >= 2:
                    new_content = " - ".join(parts[:2])
                else:
                    new_content = parts[0]
                line = f"SUMMARY:{new_content}\n"
            new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)