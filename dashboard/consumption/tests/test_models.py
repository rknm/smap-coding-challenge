from django.test import TestCase
from consumption.models import User, Data
from django.db.models.functions import TruncMonth
from django.db.models import Avg, Sum
import datetime


class UserModelTests(TestCase):

    def test_is_count(self):
        """
          初期状態では0であること
        """
        self.assertEqual(User.objects.count(), 0)

    def test_is_count_one(self):
        """
            1つレコードを作成して、レコードが1つだけカウントされること
        """
        # userデータの保存
        user = User(id=3000, area='a1', tariff='t2')
        user.save()

        # userデータの取得
        saved_users = User.objects.all()
        # カウントが1つかどうか確認
        self.assertEqual(saved_users.count(), 1)


class DataModelTests(TestCase):

    def test_is_count(self):
        """
          初期状態では0であること
        """
        self.assertEqual(Data.objects.count(), 0)

    def test_is_count_one(self):
        """
            1つレコードを作成して、レコードが1つだけカウントされること
        """
        # userデータとconsumptionデータの保存
        user = User(id=3000, area='a1', tariff='t2')
        user.save()
        data = Data(datetime='2016-07-15 00:00:00',
                    consumption=39.0, user_id=3000)
        data.save()

        # consumptionデータの取得
        saved_data = Data.objects.all()
        # カウントが1つかどうか確認
        self.assertEqual(saved_data.count(), 1)

    def test_is_relation(self):
        """
            登録データが取得できることとUserモデルとのリレーションがあるか確認
        """
        # userデータとconsumptionデータの保存
        user = User(id=3000, area='a1', tariff='t2')
        user.save()
        data = Data(datetime='2016-07-15 00:00:00',
                    consumption=39.0, user_id=3000)
        data.save()

        # userデータとconsumptionデータの取得
        saved_data = Data.objects.all()
        actual_data = saved_data[0]
        saved_user = User.objects.all()
        actual_user = saved_user[0]

        # 保存データと取得データが一致するか確認
        self.assertEqual(actual_data.datetime, datetime.datetime(
            2016, 7, 15, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(actual_data.consumption, 39.0)
        self.assertEqual(actual_data.user, actual_user)

    def test_is_grouped_by_month(self):
        """
            月単位でグルーピングしたデータの平均値と合計を確認
            7月分と8月分のデータを3件ずつ登録してそれぞれの平均値と合計を確認する
        """
        # userデータとconsumptionデータの保存
        user = User(id=3000, area='a1', tariff='t2')
        user.save()
        data_list = []
        # 7月8月のデータをそれぞれ3日分用意
        sample_date_list = ['2016-07-01 00:00:00', '2016-07-02 00:00:00', '2016-07-03 00:00:00',
                            '2016-08-01 00:00:00', '2016-08-02 00:00:00', '2016-08-03 00:00:00']
        # データを作成して挿入
        for sample_date in sample_date_list:
            data_list.append(Data(datetime=sample_date,
                                  consumption=1.0, user_id=3000))
        Data.objects.bulk_create(data_list)

        # 月単位でデータを収集する
        total_monthly_consumption = Data.objects.annotate(
            monthly_date=TruncMonth('datetime')).values('monthly_date').annotate(sum=Sum('consumption'), avg=Avg('consumption')).values('monthly_date', 'sum', 'avg').order_by('monthly_date')
        list_data = list(total_monthly_consumption)

        # 7月分と8月分のデータを取り出す
        july_data = list_data[0]
        august_data = list_data[1]

        # 7月分のデータと8月分のデータが一致するか確認
        self.assertEqual(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 3.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEqual(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 3.0)
        self.assertEqual(august_data['avg'], 1.0)

    def test_is_grouped_by_month_and_user_id_filter(self):
        """
            idによるフィルタリング+月単位でグルーピングしたデータの平均値と合計を確認
            7月分と8月分のデータを3件ずつ登録してそれぞれの平均値と合計を確認する
        """
        # userデータとconsumptionデータの保存
        user_list = [User(id=3000, area='a1', tariff='t2'),
                     User(id=3001, area='a2', tariff='t3')]
        User.objects.bulk_create(user_list)
        data_list = []
        # 7月8月のデータをそれぞれ3日分用意
        sample_date_list = ['2016-07-01 00:00:00', '2016-07-02 00:00:00', '2016-07-03 00:00:00',
                            '2016-08-01 00:00:00', '2016-08-02 00:00:00', '2016-08-03 00:00:00']
        # 3000番のユーザーのみのデータが集計できることを確認するために別IDも用意する
        user_id_list = [3000, 3001]
        # データを作成して挿入
        for user_id in user_id_list:
            for sample_date in sample_date_list:
                data_list.append(Data(datetime=sample_date,
                                      consumption=1.0, user_id=user_id))
        Data.objects.bulk_create(data_list)

        # userIDによるフィルタリング+月単位でデータを収集する
        total_monthly_consumption = Data.objects.filter(user_id=3000).annotate(
            monthly_date=TruncMonth('datetime')).values('monthly_date').annotate(sum=Sum('consumption'), avg=Avg('consumption')).values('monthly_date', 'sum', 'avg').order_by('monthly_date')
        list_data = list(total_monthly_consumption)

        # 7月分と8月分のデータを取り出す
        july_data = list_data[0]
        august_data = list_data[1]

        # 7月分のデータと8月分のデータが一致するか確認
        self.assertEqual(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 3.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEqual(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 3.0)
        self.assertEqual(august_data['avg'], 1.0)
