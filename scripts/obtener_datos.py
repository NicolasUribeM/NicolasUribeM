"""Trae de GitHub los datos que pintan las tarjetas y los deja en datos/.

Solo biblioteca estándar: lo corre el workflow sin instalar nada.

    GITHUB_TOKEN   basta para el calendario de contribuciones (es el dato público
                   del perfil; incluye las privadas si el perfil las muestra).
    PERFIL_TOKEN   opcional, con lectura de los repos privados. Solo con él se
                   recalculan los lenguajes; sin él se conserva datos/lenguajes.json
                   tal como está, con su fecha, en vez de pisarlo con solo lo público.

En local:  $env:PERFIL_TOKEN = (gh auth token); python scripts\\obtener_datos.py
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

USUARIO = os.environ.get("PERFIL_USUARIO", "NicolasUribeM")
DATOS = Path(__file__).resolve().parent.parent / "datos"

Q_CALENDARIO = """
query($u: String!) {
  user(login: $u) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""

Q_LENGUAJES = """
query($u: String!, $c: String) {
  user(login: $u) {
    repositories(first: 100, after: $c, ownerAffiliations: OWNER, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        isPrivate
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}"""


def graphql(token: str, consulta: str, variables: dict) -> dict:
    peticion = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": consulta, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "perfil-" + USUARIO},
    )
    with urllib.request.urlopen(peticion, timeout=30) as r:
        cuerpo = json.load(r)
    if cuerpo.get("errors"):
        raise SystemExit(f"GitHub respondió con errores: {cuerpo['errors']}")
    return cuerpo["data"]


def guardar(nombre: str, contenido: dict) -> None:
    DATOS.mkdir(exist_ok=True)
    (DATOS / nombre).write_text(
        json.dumps(contenido, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


def calendario(token: str, hoy: str) -> None:
    cal = graphql(token, Q_CALENDARIO, {"u": USUARIO})["user"]["contributionsCollection"][
        "contributionCalendar"
    ]
    dias = [
        {"fecha": d["date"], "n": d["contributionCount"]}
        for semana in cal["weeks"]
        for d in semana["contributionDays"]
    ]
    guardar(
        "contribuciones.json",
        {"usuario": USUARIO, "actualizado": hoy, "total": cal["totalContributions"], "dias": dias},
    )
    print(f"contribuciones: {cal['totalContributions']} en {len(dias)} días")


def lenguajes(token: str, hoy: str) -> None:
    totales: dict[str, int] = {}
    repos = privados = 0
    cursor = None
    while True:
        pagina = graphql(token, Q_LENGUAJES, {"u": USUARIO, "c": cursor})["user"]["repositories"]
        for repo in pagina["nodes"]:
            repos += 1
            privados += repo["isPrivate"]
            for arista in repo["languages"]["edges"]:
                nombre = arista["node"]["name"]
                totales[nombre] = totales.get(nombre, 0) + arista["size"]
        if not pagina["pageInfo"]["hasNextPage"]:
            break
        cursor = pagina["pageInfo"]["endCursor"]
    if not privados:
        # Un token que no ve los privados daría un reparto falso (2 repos de 11).
        print("lenguajes: el token no ve repos privados; se conserva el archivo anterior")
        return
    guardar(
        "lenguajes.json",
        {
            "actualizado": hoy,
            "repos": repos,
            "privados": privados,
            "bytes": dict(sorted(totales.items(), key=lambda kv: -kv[1])),
        },
    )
    print(f"lenguajes: {repos} repos ({privados} privados), {len(totales)} lenguajes")


def main() -> None:
    hoy = dt.datetime.now(dt.timezone.utc).date().isoformat()
    token_perfil = os.environ.get("PERFIL_TOKEN", "").strip()
    token = token_perfil or os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        sys.exit("Falta GITHUB_TOKEN o PERFIL_TOKEN en el entorno.")
    calendario(token, hoy)
    if token_perfil:
        lenguajes(token_perfil, hoy)
    else:
        print("lenguajes: sin PERFIL_TOKEN, no se tocan")


if __name__ == "__main__":
    main()
