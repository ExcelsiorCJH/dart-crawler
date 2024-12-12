import os
import re
import ssl
import random
import requests
import time

import dill
import pandas as pd

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from src.OpenDartReader import OpenDartReader
from src.utils import ProxyUserAgentManager

from dotenv import load_dotenv

load_dotenv()

ssl._create_default_https_context = ssl._create_unverified_context


class DartCrawler:
    def __init__(self):
        self.dart = OpenDartReader(os.getenv("DART_API_KEY"))
        self.proxy_user_agent_manager = ProxyUserAgentManager()

    def get_list(self, start_date: str, end_date: str, kind: str = "") -> pd.DataFrame:
        self.start_date, self.end_date = start_date, end_date
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        dfs = []

        while start < end:
            next_month = start + timedelta(days=30)
            if next_month > end:
                next_month = end

            dfs.append(
                self.dart.list(
                    start=start.strftime("%Y-%m-%d"),
                    end=next_month.strftime("%Y-%m-%d"),
                    kind=kind,
                )
            )
            start = next_month

        self.list_df = pd.concat(dfs, ignore_index=True)
        self.list_df = self.list_df.sort_values(by="rcept_dt")
        self.list_df = self.list_df.reset_index(drop=True)
        return self.list_df

    def get_document(self, list_df: pd.DataFrame, save_dir: str = "data") -> list[dict]:
        from_date, to_date = list_df.iloc[0]["rcept_dt"], list_df.iloc[-1]["rcept_dt"]
        self.data = []
        for idx, row in tqdm(list_df.iterrows(), total=len(list_df)):
            corp_code, corp_name = row["corp_code"], row["corp_name"]
            rcept_no, report_nm = row["rcept_no"], row["report_nm"]

            doc_df = self.dart.sub_docs(rcept_no)
            docs = []
            for idx, row in doc_df.iterrows():
                url = row["url"]
                title = row["title"]
                user_agent = self.proxy_user_agent_manager.get_next_proxy_user_agent()["user_agent"]
                headers = {"User-Agent": user_agent}
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(strip=False)
                text = re.sub(r"\n+", "\n", text)
                text = re.sub(r" {2,}", " ", text)

                docs.append({
                    "title": title,
                    "text": text,
                })

                time.sleep(random.uniform(0.3, 0.7))

            self.data.append(
                {
                    "corp_code": corp_code,
                    "corp_name": corp_name,
                    "report_nm": report_nm,
                    "document": docs,
                }
            )
            time.sleep(random.uniform(0.3, 0.9))

        if save_dir:
            self._save_data(self.data, from_date, to_date, save_dir)

        return self.data

    def _save_data(self, data: list[dict], from_date: str, to_date:str, save_dir: str = "data") -> None:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(
            save_dir, f"dart_report_{from_date}_{to_date}.pkl"
        )
        with open(save_path, "wb") as f:
            dill.dump(data, f)
