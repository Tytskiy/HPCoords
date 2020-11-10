class BasePlotter:
    def __init__(self, data, **unknown_variables):
        """Инициализация класса

        Parameters
        ----------
        data : Данные
            [description]
        """
        self._data_collector(data)
        self._data_validaton(data)
        self._data_handler(data)

    def _data_collector(self, data, **unknown_variables):
        """Сборщик разрозненных данных в dict(нас не интересует правильность введенных данных)

        Parameters
        ----------
        data : Возможно список из параметров, возможно "последовательность параметров" - вместо 
        "data" "x, y, z..."
            description

        Returns
        -------
        dict
            Данные собранные в dict
        """
        return collect_data

    def _data_handler(self, data, **unknown_variables):
        """Обработчик входящих данных, приводящих их в единый формат

        Parameters
        ----------
        data : dict
            Данные будут собираться в словарь, из него узнаем как пользователь передал данные

        Returns
        -------
        pd.DataFrame
            Все данные после обработки будут представленны в едином формате
        """
        return already_data

    def _data_validaton(self, data, **unknown_variables):
        return is_valid
        """Проверка данных соответствию некоторому допустимому
        формату(пропущенны ли значения, что передано)

        Parameters
        ----------
        data : dict
            Данные будут собираться в словарь, из него узнаем как пользователь передал данные

        Returns
        -------
        bool
            0 - данные не соответствуют формату, 1 - данные соответсвтуют формату
        """
