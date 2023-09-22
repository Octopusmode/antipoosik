class AFKChecker:
    def __init__(self, n, n_minutes):
        self.n = n
        self.n_minutes = n_minutes
        self.total_checks = 0
        self.false_checks = 0
        self.afk = False

    def perform_check(self):
        """
        Выполняет проверку значения.

        Возвращает:
        - bool: результат проверки (True или False)

        """
        pass

    def update_status(self):
        """
        Обновляет статус AFK на основе результатов последней проверки.

        """
        result = self.perform_check()
        self.total_checks += 1

        if not result:
            self.false_checks += 1
        else:
            self.false_checks = 0

        if self.false_checks >= (self.n_minutes * 60) / self.n:
            self.afk = True
        else:
            self.afk = False

    def is_afk(self):
        """
        Возвращает текущий статус AFK.

        Возвращает:
        - bool: True, если пользователь AFK, иначе False

        """
        return self.afk

"""
afk_checker = AFKChecker(n=10, n_minutes=3)
while True:
    # Выполняйте свои действия и вызывайте метод update_status() при необходимости
    afk_checker.update_status()

    if afk_checker.is_afk():
        print("Пользователь AFK!")
    else:
        print("Пользователь активен!")
"""