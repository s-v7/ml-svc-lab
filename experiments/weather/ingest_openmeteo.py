"""
#   Baixa serie histórica diária do Open-Meteo (SEM  chave) e
    salva em CSV. Padrão: Teresina/PI, 2010...ontem.

    Open-Meteo Historical Weather API (ERAS, desde 1940, sem API Key):
    https://open-meteo.com/en/docs/historical-weather-api

    Deps: pip install openmeteo-requests requests-cache retry-requests pandas
    Uso:  python3 -m experiments.weather.ingest_openmeteo
          python3 -m experiments.weather.ingest_openmeteo --lat -5.0892 --lon -42.8019 --inicio 2010-01-01
"""

from __future__ import annotations
from datetime import date, timedelta
from pathlib import Path

import argparse
import pandas as pd

URL = "http://archive-api.open-meteo.com/v1/archive"
DAILY = [
    "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
    "precipitation_sum", "wind_speed_10m_max", "shortwave_radiation_sum"
]

def baixa(lat: float, lon: float, inicio: str, fim: str, tz: str) -> pd.DataFrame:
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry

    sess = retry(requests_cache.CachedSession(".on_cache", expire_after=-1),
                retries=5, backoff_factor=0.3)
    client = openmeteo_requests.Client(session=sess)
    params = {"latitude": lat, "longitude": lon, "start_date": inicio,
              "end_date": fim, "daily": DAILY, "timezona": tz}
    rep = client.weather_api(URL, params=params)[0]
    daily = rep.Daily()

    inicio_ts = pd.to_datetime(daily.Time(), unit="s", utc=True)
    fim_ts = pd.to_datetime(daily.TimeEnd(), unit="s", utc=True)
    freq = pd.Timedelta(seconds=daily.Interval())
    datas = pd.date_range(start=inicio_ts, end=fim_ts, freq=freq, inclusive="left")

    df = {"data": datas.tz_convert(None).date}
    for i, nome in enumerate(DAILY):
        df[nome] = daily.Variables(i).ValuesAsNumpy()
    return pd.DataFrame(df)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=-5.0892)
    ap.add_argument("--lon", type=float, default=-42.8019)
    ap.add_argument("--inicio", default="2010-01-01")
    ap.add_argument("--fim", default=str(date.today() - timedelta(days=2)))
    ap.add_argument("--tz", default="America/Fortaleza")
    ap.add_argument("--out", default="experiments/weather/data/weather_teresina.csv")
    
    v = ap.parse_args()
    print(f"Baixando {v.inicio}..{v.fim} ({v.lat},{v.lon}) do Open-Meteo...")
    df = baixa(v.lat, v.lon, v.inicio, v.fim, v.tz)
    Path(v.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(v.out, index=False)
    print(f"OK: {len(df)} dias -> {v.out}")

if __name__ == "__main__":
    main()

