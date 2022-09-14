import vk_api
from config import TOKEN_API_VK


class api:

    def __init__(self, db):
        self.db = db
        self._vk = vk_api.VkApi(token=TOKEN_API_VK)
        self.vk = self._vk.get_api()
        self.offset = 0

    # Поиск переписывающегося пользователя с ботом и добавление в
    # БД с определёнными критериями поиска

    def user(self, user_id):
        res = self.vk.users.get(user_ids=user_id,
                                fields='country,city,sex,status,bdate')[0]
        filter = self.db.insert_user(res)
        res['filter'] = filter
        return res

    # Листание и поиск пользователей по фильтру
    def open_user(self, user_id, offset, filters, command='search'):
        count = 1
        self.offset = offset
        self.command = command
        res = self.vk.users.search(
            country=filters[0], city=filters[1], sex=filters[2],
            status=filters[3], age_from=filters[4],
            age_to=filters[5], has_photo=True, count=count, offset=self.offset)
        user_in_list = self.db.user_in_list(user_id, res['items'][0]['id'])
        if user_in_list == 'blacklist' or \
                res['items'][0]['is_closed'] is not False:
            if self.command == 'search':
                offset += 1
            elif self.command == 'search_back':
                offset -= 1
                if offset < 0:
                    command = 'search'
                    offset = 0
            elif self.command == 'search_next':
                if len(res['items'][0]) > 0:
                    offset += 1
                else:
                    offset -= 1

            if offset < 0:
                command = 'search'
                offset = 0
            return self.open_user(user_id, offset, filters, command)
        else:
            if user_in_list == 'favorites':
                res['star'] = True
            else:
                res['star'] = False
            res['offset'] = offset
            return res

    # Фильтр для поиска
    def search_filter(self, user_id):
        return self.db.search_filter(user_id)

    # Поиск людей и 3 фотографий
    def search_users(self, user_id, offset, filters, command):
        self.command = command
        self.filters = filters
        self.offset = offset
        arr_user = {}
        list_users = []
        user = self.open_user(user_id, offset, filters, command)
        res = self.vk.photos.get(
            owner_id=user['items'][0]['id'],
            album_id='profile',
            extended=True,
            photo_sizes=True
        )
        arr_photo = {}
        for photo in res['items']:
            if len(arr_photo) < 3:
                arr_photo[photo['id']] = photo['likes']['count']
            else:
                for item, val in arr_photo.items():
                    if photo['likes']['count'] > val:
                        del arr_photo[item]
                        arr_photo[photo['id']] = photo['likes']['count']
                        break
        list_photo = []
        for photo in arr_photo.keys():
            list_photo.append(f"photo{user['items'][0]['id']}_{photo}")

        arr_user1 = {}
        arr_user1['id_user'] = user['items'][0]['id']
        arr_user1['first_name'] = user['items'][0]['first_name']
        arr_user1['last_name'] = user['items'][0]['last_name']
        arr_user1['photo'] = list_photo
        list_users.append(arr_user1)

        arr_user['offset'] = user['offset']
        arr_user['star'] = user['star']
        arr_user['count'] = user['count']
        arr_user['users'] = list_users
        return arr_user

    # Добавить в лист избранных
    def insert_favorites(self, id_elected_user, user_id):
        return self.db.add_elected_user(user_id, id_elected_user, 'favorites')

    # Добавить в черный список
    def insert_blacklist(self, id_elected_user, user_id):
        return self.db.add_elected_user(user_id, id_elected_user, 'blacklist')

    # Обновить фильтр через строку
    def update_filter(self, user_id, new_filter):
        self.filter = list(map(int, new_filter.split(',')))
        self.db.update_search_filter(user_id, self.filter)
        return self.filter

    # Просмотр листа с избранными пользователями

    def view_favorites(self, user_id):
        return self.db.list_elected_user(user_id, 'favorites')

    # Просмотр листа с пользователями из чёрного списка
    def view_blacklist(self, user_id):
        return self.db.list_elected_user(user_id, 'blacklist')

    # Работа с сообщениями и последним листанием
    def worker_message(self, user_id, message_id, offset, action):
        return self.db.worker_message(user_id, message_id, offset, action)
