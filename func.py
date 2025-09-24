import requests as r
def download(week, number) -> None:
    request = r.get(f"http://www.gpu-lr.fr/gpu/gpu2vcs.php?semaine={week}&prof_etu=ETU&etudiant={number}&enseignantedt=")
    print(request)
