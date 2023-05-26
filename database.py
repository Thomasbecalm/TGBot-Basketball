import sqlite3

from geopy.distance import geodesic
from typing import List, Tuple

#class for users  and playgrounds data base
class BotDB:
    def __init__(self, db_file):
        """
        Инициализация объекта базы
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    """ Работа с юзерами """
    def user_exists(self, user_id):
        """
        Проверяем, есть ли юзер в базе
        """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """
        Достаем id юзера в базе по его user_id
        """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, username, game_level, years_exprs):
        """
        Добавляем юзера в базу
        """
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `rating`, `game_level`, `years_exprs`) VALUES (?, ?, ?, ?, ?)", (user_id, username, 0, game_level, years_exprs))
        return self.conn.commit()

    def get_info_about_user(self, user_id):
        """
        as
        """
        result = self.cursor.execute("SELECT * from `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()






    """ Работа с площадками """
    def add_court(self, user_id, name, image_id, address, lat, lng):
        """
        Define function to add a new basketball court to the database
        """
        self.cursor.execute("INSERT INTO basketball_courts (user_id, name, image_id, address, latitude, longitude, players, green_player, yellow_player, red_player, years) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (user_id, name, image_id, address, lat, lng, 0, 0, 0, 0, 0))
        self.conn.commit()
        return self.cursor.lastrowid

    # ТУТ мы ищем либо одну ближайшую площадку либо список из них
    def get_courts_nearby(self, latitude: float, longitude: float, radius: float = 5.0) ->\
            List[Tuple[int, int, str, str, str, float, float, int, int, int, int, int]]:
        """
        Возвращает список баскетбольных площадок в радиусе 1 км от заданных координат.
        """
        # "SELECT *, (6371 * acos(cos(radians(?)) * cos(radians(?)) * cos(radians(longtitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance FROM basketball_courts ORDER BY distance ASC LIMIT 1",
        self.cursor.execute(
            "SELECT *, (acos(sin(?)*sin(latitude) + cos(?)*cos(latitude)*cos(longitude-?))*6371) AS distance FROM basketball_courts WHERE distance<1000 ORDER BY distance",
            (latitude, latitude, longitude,))
        # self.cursor.execute(
        #     "SELECT *, (6371 * acos(cos(radians(?)) * cos(radians(?)) * cos(radians(longtitude) - radians(?)) + sin(radians(?)) * sin(radians(latitude)))) AS distance FROM basketball_courts ORDER BY distance",
        #     (latitude, latitude, longitude, radius))
        courts = self.cursor.fetchall()
        return courts

    def get_nearby_courts(self, user_location):
        """
        Функция для получения списка баскетбольных площадок поблизости
        """
        self.cursor.execute('SELECT * FROM basketball_courts')
        # Получаем список всех баскетбольных площадок из базы данных
        all_courts = self.cursor.fetchall()
        # Сортируем площадки по расстоянию от пользователя
        nearby_courts = sorted(all_courts, key=lambda court: geodesic(user_location, (court[3], court[4])).km)
        return nearby_courts

    def get_nearest_court(self, latitude, longitude):
        """
        Define function to get the nearest basketball court from the database
        """
        self.cursor.execute(
            "SELECT *, (acos(sin(?)*sin(latitude) + cos(?)*cos(latitude)*cos(longitude-?))*6371) AS distance FROM basketball_courts WHERE distance<0.5 ORDER BY distance ASC LIMIT 1",
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
        """
        self.cursor.execute("SELECT * FROM basketball_courts WHERE id=?", (court_id,))
        court = self.cursor.fetchone()
        return court

    def add_player_on_court(self, user_id, court_id):
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
                             latitude, longtitude, date, time, description):

        self.cursor.execute("INSERT INTO `basketball_events` (`admin_id`, `name`, `acsess`, `players_lvls`, `address`, `latitude`, `longitude`, `date`, `time`, `description`, `seted`, `continued`, `finished`, `image_id`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (admin_id, eventname, acsess, levels, address, latitude, longtitude, date, time, description, 0, 0, 0, 0,))
        return self.conn.commit()

    def get_all_events(self):
        # self.cursor.execute(
        #     "SELECT *, (acos(sin(?)*sin(latitude) + cos(?)*cos(latitude)*cos(longitude-?))*6371) AS distance FROM basketball_courts ORDER BY distance ASC LIMIT ?",
        #     (latitude, latitude, longitude, radius))
        self.cursor.execute("SELECT * FROM basketball_events")
        courts = self.cursor.fetchall()
        return courts

    def get_all_events_by_admin(self, admin_id):
        self.cursor.execute("SELECT * FROM basketball_events WHERE `admin_id`=?", (admin_id,))
        courts = self.cursor.fetchall()
        return courts

    def delete_event_by_id(self, id):
        self.cursor.execute("DELETE FROM basketball_events WHERE `id`=?", (id,))
        return self.conn.commit()

    def set_active_by_id(self, id):
        self.cursor.execute("UPDATE basketball_events SET `continued`=? WHERE id=?", (1, id))
        return self.conn.commit()

    def set_disactive_by_id(self, id):
        self.cursor.execute("UPDATE basketball_events SET `finished`=? WHERE id=?", (1, id))
        return self.conn.commit()

    # def set_active_court(self, court_id):
    #     """
    #     Define function to set a basketball court as active in the database
    #     """
    #     self.cursor.execute("UPDATE basketball_courts SET active+=1 WHERE id=?", (court_id,))
    #     self.conn.commit()
    # def get_records(self, user_id, within = "all"):
    #     """Получаем историю о доходах/расходах"""
    #     if within == "day":
    #         result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     elif within == "week":
    #         result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     elif within == "month":
    #         result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     else:
    #         result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #
    #     return result.fetchall()

    def close(self):
        """
        Закрываем соединение с БД
        """
        self.conn.close()