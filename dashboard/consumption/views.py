# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.db.models import Avg, Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, status
from rest_framework.response import Response

# Create your views here.
from .models import User, Data
from .serializer import DataSerializer


def summary(request):
    """
        次のデータを含むテンプレートを返す
        ・ユーザー一覧
        ・電力消費量の総合計、総平均
        ・電力消費量の月単位の合計、平均
    """
    users = User.objects.all().order_by('id')
    data = Data.objects.all()
    total_monthly_consumption = Data.objects.annotate(
        monthly_date=TruncMonth('datetime')).values('monthly_date').annotate(sum=Sum('consumption'), avg=Avg('consumption')).values('monthly_date', 'sum', 'avg').order_by('monthly_date')

    context = {
        'users': users,
        'sum': data.aggregate(Sum('consumption')),
        'mean': data.aggregate(Avg('consumption')),
        'totalMonthlyConsumption': list(total_monthly_consumption),

    }
    return render(request, 'consumption/summary.html', context)


def detail(request):
    """
        次のデータを含むテンプレートを返す
        ・ユーザー一覧
        ・エリア一覧
        ・料金一覧
    """
    users = User.objects.all().order_by('id')
    areas = User.objects.distinct().order_by('area').values('area')
    tariffs = User.objects.distinct().order_by('tariff').values('tariff')
    context = {
        'users': users,
        'areas': areas,
        'tariffs': tariffs
    }
    return render(request, 'consumption/detail.html', context)


"""
以下にREST用のクラスを追加
"""


class UserDataViewSet(viewsets.ModelViewSet):
    """
        RESTで返却するユーザー単位の電力消費量情報
        userIDに紐づく電力消費量
    """

    def list(self, request):
        """
            GETリクエストを解析してuserIDに紐付くデータを返します
        """
        # GETリクエストからユーザーIDを取得
        id = int(request.query_params.get('id'))
        # ユーザーIDがない場合はからデータを返す
        if not id:
            Response({'total_data': {},
                     'monthly_data': []}, status=status.HTTP_200_OK)

        # ユーザーIDに紐づく電力消費データを取得する
        data = Data.objects.filter(user_id=id).all()
        # 平均値と合計値を取得
        total_data = {'sum': data.aggregate(
            Sum('consumption')), 'avg': data.aggregate(Avg('consumption'))}
        # 月単位の集計データを取得
        monthly_data = Data.objects.filter(user_id=id).annotate(monthly_date=TruncMonth('datetime')).values(
            'monthly_date').annotate(sum=Sum('consumption'), avg=Avg('consumption')).values('monthly_date', 'sum', 'avg').order_by('monthly_date')
        return Response({'total_data': total_data, 'monthly_data': monthly_data}, status=status.HTTP_200_OK)
    # モデルのオブジェクトを取得
    queryset = Data.objects.all()
    # シリアライザーを取得
    serializer_class = DataSerializer


class OtherDataViewSet(viewsets.ModelViewSet):
    """
        RESTで返却するエリア単位または料金単位の電力消費量情報
    """

    def list(self, request):
        area = request.query_params.get('area')
        tariff = request.query_params.get('tariff')
        condition = {}
        if area:
            condition['user__area'] = area

        if tariff:
            condition['user__tariff'] = tariff
        # エリアと料金に紐づく電力消費データを取得する
        data = Data.objects.filter(**condition).all()
        # 平均値と合計値を取得
        total_data = {'sum': data.aggregate(
            Sum('consumption')), 'avg': data.aggregate(Avg('consumption'))}
        # data = Data.objects.filter(user_id=id).values()
        monthly_data = Data.objects.filter(**condition).annotate(monthly_date=TruncMonth('datetime')).values(
            'monthly_date').annotate(sum=Sum('consumption'), avg=Avg('consumption')).values('monthly_date', 'sum', 'avg').order_by('monthly_date')
        return Response({'total_data': total_data, 'monthly_data': monthly_data}, status=status.HTTP_200_OK)
    # モデルのオブジェクトを取得
    queryset = Data.objects.all()

    # シリアライザーを取得
    serializer_class = DataSerializer
