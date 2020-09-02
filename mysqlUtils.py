#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: mysqlUtils.py
@time: 2020/9/2 上午12:58
@desc:
'''
import pymysql
from settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

class MysqlClinet():
    def __init__(self):
        # Connect to the database
        self.conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                                    password=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8mb4'
                                    ) #cursorclass=pymysql.cursors.DictCursor
    def query(self, sql):
        """
        查询
        :param sql:
        :return:
        """
        try:
            with self.conn.cursor() as cursor:
                # Read a single record
                # sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
                # cursor.execute(sql, ('webmaster@python.org',))
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            return []


    def insert(self, sql,tuple_param):
        """
        数据插入
        :param sql:
        :return:
        """
        try:
            with self.conn.cursor() as cursor:
                # Create a new record
                # sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
                # cursor.execute(sql, ('webmaster@python.org', 'very-secret'))
                cursor.execute(sql, tuple_param)
            self.conn.commit()

        except:
            return []