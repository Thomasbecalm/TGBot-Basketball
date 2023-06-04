import sqlite3

from geopy.distance import geodesic
from typing import List, Tuple
from math import radians
import geopy.distance

class BotDB:
    def __init__(self, db_file):
        """
        Инициализация объекта базы
        :param str db_file: path to file
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()


    """ Работа с юзерами """
    def user_exists(self, user_id):
        """
        Проверяем, есть ли юзер в базе
        :param int user_id: ID of user
        :return: true or false
        """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """
        Достаем id юзера из базы по его user_id
        :param int user_id: ID of user
        :return: user's id
        """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, username, game_level, years_exprs):
        """
        Добавляем юзера в базу
        :param int user_id: ID of user
        :param str username: nickname of user
        :param str game_level: level of user like player
        :param int years_exprs: years of playing basketball
        :return: result of commit exchanges
        """
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `rating`, `game_level`, `years_exprs`) VALUES (?, ?, ?, ?, ?)", (user_id, username, 0, game_level, years_exprs))
        return self.conn.commit()

    def get_info_about_user(self, user_id):
        """
        Достаем всю информацию о пользователя из базы по его user_id
        :param int user_id: ID of user
        :return: All information
        """
        result = self.cursor.execute("SELECT * from `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()


    """ Работа с площадками """
    def add_court(self, user_id, name, image_id, address, lat, lng):
        """
        Добавление новой площадки в базу
        :param int user_id: ID of user
        :param str name: Nickname of court
        :param str image_id: ID of file
        :param str address: Address of court
        :param int lat: latitude
        :param int lng: longitude
        :return: id of new court
        """
        self.cursor.execute("INSERT INTO basketball_courts (user_id, name, image_id, address, latitude, longitude, players, green_player, yellow_player, red_player, years) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (user_id, name, image_id, address, lat, lng, 0, 0, 0, 0, 0))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_courts_nearby(self, latitude: float, longitude: float, radius: float = 5.0) ->\
            List[Tuple[int, int, str, str, str, float, float, int, int, int, int, int]]:
        """
        Достаем список баскетбольных площадок в радиусе 1 км от заданных координат.
        :param float latitude: latitude
        :param float longitude: longitude
        :param float radius: radius
        :return: list of coutrs
        """
        # "SELECT *, (6371 * acos(cos(radians(?)) * cos(radians(?)) * cos(radians(longtitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance FROM basketball_courts ORDER BY distance ASC LIMIT 1",
        self.cursor.execute(
            "SELECT *, (acos(sin(radians(?))*sin(radians(latitude)) + cos(radians(?))*cos(radians(latitude))*cos(radians(longitude)-radians(?)))*6371) AS distance FROM basketball_courts WHERE distance<3 ORDER BY distance",
            (latitude, latitude, longitude,))
        # self.cursor.execute(
        #     "SELECT *, (6371 * acos(cos(radians(?)) * cos(radians(?)) * cos(radians(longtitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance FROM basketball_courts ORDER BY distance",
        #     (latitude, latitude, longitude, radius))
        courts = self.cursor.fetchall()
        return courts

    def get_nearby_courts(self, user_location):
        """
        Функция для получения списка баскетбольных площадок поблизости
        :param message user_location: latitude and longitude
        :return: sorted list of courts
        """
        self.cursor.execute('SELECT * FROM basketball_courts')
        all_courts = self.cursor.fetchall()
        nearby_courts = sorted(all_courts, key=lambda court: geodesic(user_location, (court[3], court[4])).km)
        return nearby_courts

    def get_nearest_court(self, latitude, longitude):
        """
        Достаем ближайшую площадку в момент нахождения на корте
        :param float latitude: latitude
        :param float longitude: longitude
        :return: one nearest court
        """
        self.cursor.execute(
            "SELECT *, (acos(sin(radians(?))*sin(radians(latitude)) + cos(radians(?))*cos(radians(latitude))*cos(radians(longitude)-radians(?)))*6371) AS distance FROM basketball_courts WHERE distance<0.05 ORDER BY distance",
            (latitude, latitude, longitude,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        else:
            return {"id": row[0], "user_id": row[1], "name": row[2], "image_id": row[3], "address": row[4], "latitude": row[5],
                    "longitude": row[6], "players": row[7], "green_player": row[8], "yellow_player": row[9], "red_player": row[10],
                    "years": row[11]}

    def get_court_by_id(self, court_id: int) -> Tuple[int, str, str, str, float, float, int, int, int, int, int]:
        """
        Возвращает информацию о баскетбольной площадке по ее идентификатору.
        :param int court_id: ID of court
        :return: list of information
        """
        self.cursor.execute("SELECT * FROM basketball_courts WHERE id=?", (court_id,))
        court = self.cursor.fetchone()
        return court

    def add_player_on_court(self, user_id, court_id):
        """
        Добавление человека на площадку
        :param int user_id: ID of user
        :param int court_id: ID of court
        :return: result if commit
        """
        user_info = self.get_info_about_user(user_id)
        court_info = self.get_court_by_id(court_id)
        self.cursor.execute("UPDATE basketball_courts SET players=? WHERE id=?", ((court_info[7] + 1), court_id,))
        if (user_info[4] == "lovely_play"):
            self.cursor.execute("UPDATE basketball_courts SET green_player=? WHERE id=?", ((court_info[8] + 1), court_id,))
        elif (user_info[4] == "middle_play"):
            self.cursor.execute("UPDATE basketball_courts SET yellow_player=? WHERE id=?", ((court_info[9] + 1), court_id,))
        else:
            self.cursor.execute("UPDATE basketball_courts SET red_player=? WHERE id=?", ((court_info[10] + 1), court_id,))

        self.cursor.execute("UPDATE basketball_courts SET years=? WHERE id=?", (user_info[5], court_id,))
        return self.conn.commit()

    def exit_player_from_court(self, user_id, court_id):
        """
        Выход человека с площадки
        :param int user_id: ID of user
        :param int court_id: ID of court
        :return: result of commit
        """
        user_info = self.get_info_about_user(user_id)
        court_info = self.get_court_by_id(court_id)
        self.cursor.execute("UPDATE basketball_courts SET players=? WHERE id=?", ((court_info[7] - 1), court_id))
        if (user_info[4] == "lovely_play"):
            self.cursor.execute("UPDATE basketball_courts SET green_player=? WHERE id=?", ((court_info[8] - 1), court_id))
        elif (user_info[4] == "middle_play"):
            self.cursor.execute("UPDATE basketball_courts SET yellow_player=? WHERE id=?", ((court_info[9] - 1), court_id))
        else:
            self.cursor.execute("UPDATE basketball_courts SET red_player=? WHERE id=?", ((court_info[10] - 1), court_id))

        self.cursor.execute("UPDATE basketball_courts SET years=? WHERE id=?", (user_info[5], court_id))
        return self.conn.commit()


    """ Работа с ивентами """
    def add_basketball_event(self, admin_id, eventname, acsess, levels, address,
                             latitude, longitude, date, time, description):
        """
        Добавление в базу баскетбольного мероприятия
        :param int admin_id: IF of creator
        :param str eventname: eventname
        :param str acsess: acsess to event
        :param str levels: levels of players
        :param str address: address of event
        :param int latitude: latitude
        :param int longitude: longitude
        :param str date: date of start
        :param str time: time of start
        :param str description: description
        :return: result of commit
        """
        self.cursor.execute("INSERT INTO `basketball_events` (`admin_id`, `name`, `acsess`, `players_lvls`, `address`, `latitude`, `longitude`, `date`, `time`, `description`, `seted`, `continued`, `finished`, `image_id`, `players`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (admin_id, eventname, acsess, levels, address, latitude, longitude, date, time, description, 0, 0, 0, 0, 1))
        return self.conn.commit()

    def get_all_events(self):
        """
        Достаем полный список мероприятий
        :return: list of courts
        """
        # self.cursor.execute(
        #     "SELECT *, (acos(sin(?)*sin(latitude) + cos(?)*cos(latitude)*cos(longitude-?))*6371) AS distance FROM basketball_courts ORDER BY distance ASC LIMIT ?",
        #     (latitude, latitude, longitude, radius))
        self.cursor.execute("SELECT * FROM basketball_events")
        courts = self.cursor.fetchall()
        return courts

    def get_all_events_by_admin(self, admin_id):
        """
        Достаем из базы все ивенты созданные пользователем с id = admin_id
        :param int admin_id: ID of creator
        :return: list courts
        """
        self.cursor.execute("SELECT * FROM basketball_events WHERE `admin_id`=?", (admin_id,))
        courts = self.cursor.fetchall()
        return courts

    def delete_event_by_id(self, id):
        """
        Удаляем ивент из базы данных
        :param int id: id of event
        :return: result of commit
        """
        self.cursor.execute("DELETE FROM basketball_events WHERE `id`=?", (id,))
        return self.conn.commit()

    def set_active_by_id(self, id):
        """
        Устанавливаем активный статус ивента
        :param int id: id of event
        :return: result of commit
        """
        self.cursor.execute("UPDATE basketball_events SET `continued`=? WHERE id=?", (1, id))
        return self.conn.commit()

    def set_disactive_by_id(self, id):
        """
        Устанавливаем завершенный статус ивента
        :param int id: id of event
        :return: result of commit
        """
        self.cursor.execute("UPDATE basketball_events SET `finished`=? WHERE id=?", (1, id))
        return self.conn.commit()

    def get_event_by_id(self, event_id):
        """

        :param event_id:
        :return:
        """
        self.cursor.execute("SELECT * FROM `basketball_events` WHERE `id`=?", (event_id,))
        event = self.cursor.fetchone()
        return event

    def add_player_on_event(self, user_id, event_id):
        """

        :param user_id:
        :param event_id:
        :return:
        """
        event_info = self.get_event_by_id(event_id)
        print(event_id)
        print(event_info[15])
        print(event_info[0])
        players = 1
        self.cursor.execute("UPDATE basketball_events SET players=? WHERE id=1", (event_id,))
        res = self.conn.commit
        return res


    def close(self):
        """
        Закрываем соединение с БД
        """
        self.conn.close()