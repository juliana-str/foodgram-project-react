import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()

        cursor.execute("""select * from sqlite_master
                    where type = 'table'""")
        tables = cursor.fetchall()

        for table in tables:
            print(table)