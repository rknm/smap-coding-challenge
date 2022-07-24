import datetime
from django.test import RequestFactory, TestCase
from consumption.models import User, Data
from ..views import UserDataViewSet, OtherDataViewSet


class APIViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
            テスト用データのセットアップ
        """
        # userデータとconsumptionデータの保存
        user_list = [User(id=3000, area='a1', tariff='t1'),
                     User(id=3001, area='a1', tariff='t2'),
                     User(id=3002, area='a1', tariff='t3'),
                     User(id=3003, area='a2', tariff='t1'),
                     User(id=3004, area='a2', tariff='t2'),
                     User(id=3005, area='a2', tariff='t3'),
                     User(id=3006, area='a1', tariff='t1'),
                     User(id=3007, area='a2', tariff='t2')]
        User.objects.bulk_create(user_list)
        # 7月8月のデータをそれぞれ3日分用意
        sample_date_list = ['2016-07-01 00:00:00', '2016-07-02 00:00:00', '2016-07-03 00:00:00',
                            '2016-08-01 00:00:00', '2016-08-02 00:00:00', '2016-08-03 00:00:00']
        # 複数のユーザーIDを用意する
        user_id_list = [3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007]
        data_list = []
        # データを作成して挿入
        for user_id in user_id_list:
            for sample_date in sample_date_list:
                data_list.append(Data(datetime=sample_date,
                                      consumption=1.0, user_id=user_id))
        Data.objects.bulk_create(data_list)

    def test_api_userdata(self):
        """
            api/userdata のレスポンスのテスト
            3000番のユーザーの電力消費量が月単位になっていることと
            合計値が3、平均値が1であることを確認する
        """

        factory = RequestFactory()
        view = UserDataViewSet.as_view({'get': 'list'})
        url = "api/userdata?id=3000"
        request = factory.get(url)
        response = view(request)

        # 7月分と8月分のデータを取り出す
        july_data = response.data['monthly_data'][0]
        august_data = response.data['monthly_data'][1]

        self.assertEquals(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 3.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEquals(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 3.0)
        self.assertEqual(august_data['avg'], 1.0)

    def test_api_otherdata_area_a1(self):
        """
            api/otherdata のレスポンスのテスト
            エリアa1の電力消費量が月単位になっていることと
            合計値が12、平均値が1であることを確認する
        """

        factory = RequestFactory()
        view = OtherDataViewSet.as_view({'get': 'list'})
        url = "api/otherdata?area=a1"
        request = factory.get(url)
        response = view(request)

        # 7月分と8月分のデータを取り出す
        july_data = response.data['monthly_data'][0]
        august_data = response.data['monthly_data'][1]

        self.assertEquals(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 12.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEquals(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 12.0)
        self.assertEqual(august_data['avg'], 1.0)

    def test_api_otherdata_tariff_t1(self):
        """
            api/otherdata のレスポンスのテスト
            料金t1の電力消費量が月単位になっていることと
            合計値が9、平均値が1であることを確認する
        """

        factory = RequestFactory()
        view = OtherDataViewSet.as_view({'get': 'list'})
        url = "api/otherdata?tariff=t1"
        request = factory.get(url)
        response = view(request)

        # 7月分と8月分のデータを取り出す
        july_data = response.data['monthly_data'][0]
        august_data = response.data['monthly_data'][1]

        self.assertEquals(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 9.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEquals(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 9.0)
        self.assertEqual(august_data['avg'], 1.0)

    def test_api_otherdata_area_a1_tariff_t1(self):
        """
            api/otherdata のレスポンスのテスト
            エリアa1、料金t1の電力消費量が月単位になっていることと
            合計値が6、平均値が1であることを確認する
        """

        factory = RequestFactory()
        view = OtherDataViewSet.as_view({'get': 'list'})
        url = "api/otherdata?area=a1&tariff=t1"
        request = factory.get(url)
        response = view(request)

        # 7月分と8月分のデータを取り出す
        july_data = response.data['monthly_data'][0]
        august_data = response.data['monthly_data'][1]

        self.assertEquals(july_data['monthly_date'], datetime.datetime(
            2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(july_data['sum'], 6.0)
        self.assertEqual(july_data['avg'], 1.0)
        self.assertEquals(august_data['monthly_date'], datetime.datetime(
            2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(august_data['sum'], 6.0)
        self.assertEqual(august_data['avg'], 1.0)
