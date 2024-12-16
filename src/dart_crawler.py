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

    def get_document(
        self, list_df: pd.DataFrame, save_dir: str = "data", batch_size: int = 10
    ) -> list[dict]:
        self.data = []
        current_batch = []

        try:
            for idx, row in tqdm(list_df.iterrows(), total=len(list_df)):
                try:
                    corp_code, corp_name = row["corp_code"], row["corp_name"]
                    rcept_no, report_nm = row["rcept_no"], row["report_nm"]

                    # 배치의 첫 번째 항목이면 from_date 저장
                    if len(current_batch) == 0:
                        batch_from_date = row["rcept_dt"]

                    doc_df = self.dart.sub_docs(rcept_no)
                    docs = []

                    for _, doc_row in doc_df.iterrows():
                        try:
                            url = doc_row["url"]
                            title = doc_row["title"]
                            user_agent = self.proxy_user_agent_manager.get_next_proxy_user_agent()[
                                "user_agent"
                            ]
                            headers = {"User-Agent": user_agent}
                            response = requests.get(url, headers=headers)
                            soup = BeautifulSoup(response.text, "html.parser")
                            text = soup.get_text(strip=False)
                            text = re.sub(r"\n+", "\n", text)
                            text = re.sub(r" {2,}", " ", text)

                            docs.append(
                                {
                                    "title": title,
                                    "text": text,
                                }
                            )

                            time.sleep(random.uniform(0.3, 0.7))
                        except Exception as e:
                            print(f"문서 크롤링 중 오류 발생: {e} - URL: {url}")
                            continue

                    current_doc = {
                        "corp_code": corp_code,
                        "corp_name": corp_name,
                        "report_nm": report_nm,
                        "document": docs,
                    }

                    current_batch.append(current_doc)
                    self.data.append(current_doc)
                    batch_to_date = row[
                        "rcept_dt"
                    ]  # 현재 처리 중인 날짜를 to_date로 저장

                    # batch_size 단위로 저장
                    if len(current_batch) >= batch_size:
                        if save_dir:
                            self._save_batch(
                                current_batch, save_dir, batch_from_date, batch_to_date
                            )
                        current_batch = []

                    time.sleep(random.uniform(0.3, 0.9))

                except Exception as e:
                    print(f"데이터 처리 중 오류 발생: {e} - 기업명: {corp_name}")
                    if current_batch:  # 에러 발생 시 현재 배치 저장
                        self._save_batch(
                            current_batch, save_dir, batch_from_date, batch_to_date
                        )
                    current_batch = []
                    continue

        except Exception as e:
            print(f"전체 처리 중 오류 발생: {e}")
            if current_batch:  # 에러 발생 시 현재 배치 저장
                self._save_batch(
                    current_batch, save_dir, batch_from_date, batch_to_date
                )
        finally:
            # 마지막 배치 저장
            if current_batch and save_dir:
                self._save_batch(
                    current_batch, save_dir, batch_from_date, batch_to_date
                )

        return self.data

    def _save_batch(
        self, batch: list[dict], save_dir: str, from_date: str, to_date: str
    ) -> None:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        base_filename = f"dart_report_{from_date}_{to_date}.pkl"
        save_path = os.path.join(save_dir, base_filename)

        # 파일이 이미 존재하는 경우 버전 넘버 추가
        version = 0
        while os.path.exists(save_path):
            version += 1
            filename = f"dart_report_{from_date}_{to_date}_v{version}.pkl"
            save_path = os.path.join(save_dir, filename)

        try:
            with open(save_path, "wb") as f:
                dill.dump(batch, f)
            print(f"배치 저장 완료: {save_path} (기간: {from_date} ~ {to_date})")
        except Exception as e:
            print(f"배치 저장 중 오류 발생: {e}")
