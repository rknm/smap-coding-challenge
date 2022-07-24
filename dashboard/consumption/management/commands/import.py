from django.core.management.base import BaseCommand
import glob
import os
import sqlite3
import pandas as pd


class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        # ユーザーデータをインポートする
        Command._import_consumption_user()
        # 電力消費量データをインポートする
        Command._import_consumption_data()

    def _import_consumption_user():
        """
        ユーザーデータをDBへインポートします
        data/user_data.csvを読み込んでDBへ挿入します
        """
        # csvファイルパスを定義
        path = '/app/data/user_data.csv'
        # csvファイルを読み込んでDataFrameを作成する
        consumption_user_df = pd.read_csv(path)
        # SQliteとのコネクションを生成する
        conn = sqlite3.connect('/app/dashboard/db.sqlite3')

        # データベースにDataFrameを投入する
        # チャンクを設定して細かい単位で挿入する
        consumption_user_df.to_sql(
            'consumption_user', conn, if_exists='append', index=None)

    def _import_consumption_data():
        """
        電力消費量データをDBへインポートします
        data/consumption/配下にあるCSVファイルを読み込んでDBへ挿入します
        """
        # csvファイルパスを定義
        path = '/app/data/consumption/*.csv'
        files = glob.glob(path)

        # dataディレクトリ下のcsvファイルを読み込む
        # 最後に結合するためのリストを用意
        data_list = []
        for file_path in files:
            # csvファイルパスから拡張子なしのcsvファイル名を取り出す
            id = os.path.splitext(os.path.basename(file_path))[0]
            # csvファイルを読み込んでDataFrameを作成する
            consumption_data_df = pd.read_csv(file_path)
            # id列を追加する
            consumption_data_df['user_id'] = id
            # DataFrameをリストに追加
            data_list.append(consumption_data_df)

        # リストに格納したDataFrameを結合する
        dataset = pd.concat(data_list)

        # SQliteとのコネクションを生成する
        conn = sqlite3.connect('/app/dashboard/db.sqlite3')

        # データベースにDataFrameを投入する
        # チャンクを設定して細かい単位で挿入する
        dataset.to_sql('consumption_data', conn, if_exists='append',
                       index=None, method='multi', chunksize=5000)
