from datetime import datetime

import peewee as pw

db = pw.SqliteDatabase('hotel_bot.db')
db.connect()


class History(pw.Model):
    telegram_id = pw.IntegerField()
    user_name = pw.CharField()
    # user= pw.ForeignKeyField(User, backref='histories')
    command_name = pw.TextField()
    city = pw.TextField()
    hotel_name = pw.TextField()
    created_at = pw.DateTimeField(default=datetime.now())

    class Meta:
        database = db


db.create_tables([History])

