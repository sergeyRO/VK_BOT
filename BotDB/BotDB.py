import json
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from config import DSN
from BotDB.model import create_tables,\
    Users, ElectedUsers, Filters,\
    Lists, SearchValues, LastMessages
import os.path


class BotDB:
    def __init__(self):
        engine = sqlalchemy.create_engine(DSN)
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)
        session = self.Session()
        lists = session.query(Lists).count()
        filt = session.query(Filters).count()
        if lists == 0 or filt == 0:
            script_dir = os.path.dirname(sys.argv[0]) + '/BotDB'
            with open(os.path.join(script_dir, 'data.json'), 'rt') as f:
                data = json.load(f)
            for item in data:
                model = {
                    'list': Lists,
                    'filter': Filters
                }.get(item['model'])
                session.add(model(id=item.get('pk'), **item.get('fields')))
            session.commit()
        session.close()

    '''Добавление нового пользователя,
    который начал общаться с ботом + создание фильтра под его параметры'''
    def insert_user(self, user_data):
        session = self.Session()
        count_user = session.query(
            Users).filter(Users.id == user_data['id']).count()
        if count_user == 0:
            session.add(Users(id=user_data['id'], token=user_data['id']))
            filters = session.query(Filters).all()
            for item in filters:
                if item.code_filter == 'city' or item.code_filter == 'country':
                    val = user_data[item.code_filter]['id']
                elif item.code_filter == 'sex':
                    val = 0
                elif item.code_filter == 'status':
                    val = ''
                elif item.code_filter == 'age_from':
                    try:
                        val = relativedelta(
                            datetime.now(),
                            datetime.strptime(user_data['bdate'],
                                              '%d.%m.%Y')).years
                    except ValueError:
                        val = 18
                elif item.code_filter == 'age_to':
                    val = ''
                else:
                    val = ''
                session.add(
                    SearchValues(
                        id_user=user_data['id'],
                        id_filter=item.id,
                        value=val))
            print(f"Insert User {user_data['id']} and ADD SearchFilter")
        session.commit()
        session.close()
        return self.search_filter(user_data['id'])

    # Логика сохранения последнего сообщения и сдвига листания фоток
    def worker_message(self, user_id, message_id, offset, action):
        session = self.Session()
        if action == 'insert':
            session.add(
                LastMessages(id_user=user_id,
                             id_message=message_id,
                             offset=offset))
            session.commit()
            session.close()
            return message_id
        elif action == 'drop':
            id_mess = session.query(LastMessages) \
                .filter(LastMessages.id_user == user_id) \
                .order_by(LastMessages.id.desc()).first()
            session.commit()
            if id_mess:
                i = id_mess.id_message
                session.delete(id_mess)
                session.commit()
            else:
                i = 0
            session.close()
            return i

    # Логика сохранения найденного пользователя в листы
    def add_elected_user(self, user_id, elected_user, name_list='favorites'):
        session = self.Session()

        user_in_list_count = session.query(ElectedUsers) \
            .filter(ElectedUsers.id_user == user_id) \
            .filter(ElectedUsers.id_elected_user == elected_user).count()

        if user_in_list_count == 0:
            session.add(
                ElectedUsers(id_elected_user=elected_user,
                             id_user=user_id,
                             id_list=session.query(Lists.id).filter(
                                 Lists.name == name_list).first().id))
        else:
            return False
        session.commit()
        session.close()
        return self.list_elected_user(user_id, name_list)

    # Обновление фильтра от начального
    def update_search_filter(self, user_id, filters):
        # Логика изменения фильтра поиска
        i = 0
        session = self.Session()
        for item in filters:
            i += 1
            session.query(
                SearchValues).filter(SearchValues.id_user == user_id) \
                .filter(SearchValues.id_filter == i).update({'value': item})
        session.commit()
        session.close()
        return self.search_filter(user_id)

    # Собрать фильтр для поиска
    def search_filter(self, user_id):
        list_search = []
        session = self.Session()
        search = session.query(
            SearchValues).filter(SearchValues.id_user == user_id).all()
        if len(search) > 0:
            for item in search:
                list_search.append(item.value)
        else:
            filters = session.query(Filters).count()
            for item in range(filters):
                list_search.append('')
        session.commit()
        session.close()
        return list_search

    # Вывести пользователей из того или иного листа
    def list_elected_user(self, user_id, name_list):
        list_query = []
        session = self.Session()
        user_list = session.query(ElectedUsers.id_elected_user) \
            .join(Lists, ElectedUsers.id_list == Lists.id) \
            .filter(ElectedUsers.id_user == user_id) \
            .filter(Lists.name == name_list).all()
        session.commit()
        session.close()

        for item in user_list:
            list_query.append(item.id_elected_user)

        return list_query

    # Проверка нахождения пользователя в том или ином листе
    def user_in_list(self, user_id, elected_user):
        session = self.Session()
        user_in_list = session.query(
            ElectedUsers.id_elected_user, Lists.name) \
            .join(Lists, ElectedUsers.id_list == Lists.id) \
            .filter(ElectedUsers.id_user == user_id) \
            .filter(ElectedUsers.id_elected_user == elected_user).first()
        session.commit()
        session.close()
        if user_in_list is not None:
            return user_in_list.name
        else:
            return True

    ''' Определение последнего сообщения от бота
    к пользователю для последующего его удаления
    '''
    def offset(self, user_id):
        session = self.Session()
        res = session.query(LastMessages) \
            .filter(LastMessages.id_user == user_id) \
            .order_by(LastMessages.id.desc()).first()
        session.commit()
        session.close()
        if res:
            return res.offset
        else:
            return 0
