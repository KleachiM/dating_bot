from collections import Counter
from datetime import datetime
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import re

from d_base import User, session, DatingUser, Photo, add_f, Base, engine

Base.metadata.create_all(engine)

class VkBot:
    def __init__(self, gr_token, usr_token):
        self.group_token = gr_token
        self.user_token = usr_token
        self.create_longpoll()
        # self.bot_session()
        # self.user_answer()

    def create_longpoll(self):  # создание сессии для бота
        self.vk_usr = vk_api.VkApi(token=self.user_token)
        self.vk = vk_api.VkApi(token=self.group_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):  # написать сообщение пользователю
        self.vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})

    def get_l_range_from_user(self, user_id):
        message = 'Укажите нижнюю границу возрастного диапазона (число)'
        self.write_msg(user_id, message)
        try:
            return int(self.user_answer()[1])
        except:
            message = 'Неверный формат данных. Попробуйте еще раз'
            self.write_msg(user_id, message)

    def get_h_range_from_user(self, user_id):
        message = 'Укажите верхнюю границу возрастного диапазона (число)'
        self.write_msg(user_id, message)
        try:
            return int(self.user_answer()[1])
        except:
            message = 'Неверный формат данных. Попробуйте еще раз'
            self.write_msg(user_id, message)

    def get_city(self, city_title):  # получить ID города по названию
        res = self.vk_usr.method('database.getCities', {'country_id': 1, 'q': city_title})
        s = ''
        for town in res['items']:
            s += f'{town["id"]}, '
        return s[0:-2]

    def get_sex(self, sex):  # получить ID пола по названию
        if sex == 'мужчина' or sex == 'Мужчина':
            return 2
        elif sex == 'женщина' or sex == 'Женщина':
            return 1
        else:
            return 0

    def get_status(self, user_id):  # получить ID статуса по названию
        status = ''
        while not status:
            message = 'Укажите семейное положение. Варианты: \n' \
                      'не женат ' \
                      'не замужем\n' \
                      'встречается\n' \
                      'помолвлен ' \
                      'помолвлена\n' \
                      'женат ' \
                      'замужем\n' \
                      'все сложно\n' \
                      'в активном поиске\n' \
                      'влюблен ' \
                      'влюблена\n' \
                      'в гражданском браке'
            self.write_msg(user_id, message)
            status = self.user_answer()[1]
            if re.findall('[Н,н]е женат|[Н,н]е замужем', status) and status == \
                    re.findall('[Н,н]е женат|[Н,н]е замужем', status)[0]:
                return 1
            elif re.findall('[В,в]стречается', status) and status == re.findall('[В,в]стречается', status)[0]:
                return 2
            elif re.findall('[П,п]омолвлен[а]', status) and status == re.findall('[П,п]омолвлен[а]', status)[0]:
                return 3
            elif re.findall('[Ж,ж]енат', status) and status == re.findall('[Ж,ж]енат', status)[0]:
                return 4
            elif re.findall('[З,з]амужем', status) and status == re.findall('[З,з]амужем', status)[0]:
                return 4
            elif re.findall('[В,в]се сложно', status) and status == re.findall('[В,в]се сложно', status)[0]:
                return 5
            elif re.findall('[В,в] активном поиске', status) and status == re.findall('[В,в] активном поиске', status)[0]:
                return 6
            elif re.findall('[В,в]люблен[а]', status) and status == re.findall('[В,в]люблен[а]', status)[0]:
                return 7
            elif re.findall('[В,в] гражданском браке', status) and status == \
                    re.findall('[В,в] гражданском браке', status)[0]:
                return 8

    def user_answer(self):  # получить ответ пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    user_id = event.user_id
                    break
        return user_id, request

    def get_query_param(self, searcher_id):  # получить параметры для поиска пользователей
        # searcher_id = self.user_answer()[0]
        query = {'age_from': '', 'age_to': '', 'city': '', 'sex': '', 'status': '', 'fields': 'bdate'}
        while True:
            age_from = self.get_l_range_from_user(searcher_id)
            if age_from:
                query['age_from'] = age_from
                break
        while True:
            age_to = self.get_h_range_from_user(searcher_id)
            if age_to:
                query['age_to'] = age_to
                break
        self.write_msg(searcher_id, 'Укажите город для поиска')
        query['city'] = self.get_city(self.user_answer()[1])
        self.write_msg(searcher_id, 'Укажите пол. Варианты: мужчина, женщина, любой')
        query['sex'] = self.get_sex(self.user_answer()[1])
        query['status'] = self.get_status(searcher_id)
        if not session.query(User).filter(User.id == searcher_id).all():  # внесение в базу данных инфы о пользователе
            user = self.vk_usr.method('users.get', {'user_ids': searcher_id, 'fields': 'bdate, sex, city'})[0]
            # age = (datetime.now() - datetime.strptime(user['bdate'], "%d.%m.%Y")).days/365.2425
            searcher = User(
                id=searcher_id,
                name=user['first_name'],
                second_name=user['last_name'],
                age=self.get_user_age(user['bdate']),
                age_range_from=query['age_from'],
                age_range_to=query['age_to'],
                sex='мужчина' if user['sex'] == 2 else 'женщина',
                city=user['city']['title']
            )
            add_f(searcher)
        return query

    def users_search(self, query_param):  # поиск пользователей по параметрам
        res = self.vk_usr.method('users.search', query_param)
        return res

    def get_user_age(self, bdate):  # получить возраст пользователя
        try:
            return int((datetime.now()-datetime.strptime(bdate, "%d.%m.%Y")).days/365.2425)
        except:
            return 'неизвестно'

    def vk_search(self):  # поиск пользователей и добавление в бд
        searcher_id = self.user_answer()[0]
        query_param = self.get_query_param(searcher_id)
        users = self.users_search(query_param)
        for user in users['items']:
            if user['can_access_closed'] and 'bdate' in user and re.findall('[0-9]{1,2}.[0-9]{1,2}.\d{4}', user['bdate']):
                if not session.query(DatingUser).filter(DatingUser.id == user['id']).all():
                    self.write_msg(searcher_id,
                                   f'Вам нравится пользователь: \n'
                                   f'{user["first_name"]} {user["last_name"]}, '
                                   f'возраст: {self.get_user_age(user["bdate"])}? \n'
                                   f'(да/нет/стоп)'
                                   )
                    answer = self.user_answer()[1]
                    if re.findall('[Д,д]а', answer) and answer == re.findall('[Д,д]а', answer)[0]:
                        if not session.query(DatingUser).filter(DatingUser.id == user['id']).all():
                            datinguser = DatingUser(  # добавление пользователя в таблицу datingUser
                                id=user['id'],
                                name=user['first_name'],
                                second_name=user['last_name'],
                                age=self.get_user_age(user['bdate']),
                                user_id=searcher_id
                            )
                            add_f(datinguser)
                            photos = self.vk_usr.method('photos.get', {'owner_id': user['id'], 'album_id': 'profile', 'extended': 1})
                            temp_photos_dict = {}
                            for photo in photos['items']:
                                temp_photos_dict.setdefault(photo['id'], photo['likes']['count'])
                            max3_photos = dict(Counter(temp_photos_dict).most_common(3))
                            for photo in max3_photos:
                                photo_inf = self.vk_usr.method('photos.getById', {'photos': f'{user["id"]}_{photo}', 'extended': 0})
                                photo_ins = Photo(  # добавление фото в таблицу Photo
                                    id=photo,
                                    link=photo_inf[0]['sizes'][len(photo_inf[0]['sizes']) - 1]['url'],
                                    likes_count=max3_photos.get(photo),
                                    dating_id=user['id']
                                )
                                add_f(photo_ins)
                    elif re.findall('[Н,н]ет', answer) and answer == re.findall('[Н,н]ет', answer)[0]:
                        continue
                    elif re.findall('[С,с]топ', answer) and answer == re.findall('[С,с]топ', answer)[0]:
                        break
                    else:
                        self.write_msg(searcher_id, 'Ваш ответ мне не понятен')
                        break
        self.write_msg(searcher_id, 'Показать понравившихся пользователей?\n(да/нет)')
        answer = self.user_answer()[1]
        if re.findall('[Д,д]а', answer) and answer == re.findall('[Д,д]а', answer)[0]:
            self.users_show(searcher_id)

    def users_show(self, id):
        users = session.query(DatingUser).all()
        for user in users:
            users_photo = session.query(Photo).filter(Photo.dating_id==user.id)
            self.write_msg(id, f'Вам понравился пользователь: \n'
                                f'{user.name} {user.second_name}, возраст: {user.age}')
            for photo in users_photo:
                self.write_msg(id, f'{photo.link}')
            self.write_msg(id, 'Показать следующего пользователя? (да/стоп)')
            answer = self.user_answer()[1]
            if re.findall('[Д,д]а', answer) and answer == re.findall('[Д,д]а', answer)[0]:
                continue
            else:
                break

