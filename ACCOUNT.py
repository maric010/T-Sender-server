import os
path = os.getcwd()
class ACCOUNT:
    'Это класс АККАУНТА'
    # Способ создания объекта (конструктор)
    def __init__(self):
        self.username = ""
        self.firstname = ""
        self.lastname = ""
        self.password = ""
        self.email=""
        self.balance="0"
        self.path = ""
        self.admin = False
        self.telegram_accounts = []
        self.new_telegram_account=None
class TELEGRAM_ACCOUNT:
    'Это класс ТЕЛЕГРАММ АККАУНТА'
    # Способ создания объекта (конструктор)
    def __init__(self):
        self.client = None
        self.phone = ""

class testik:
    'Это класс АККАУНТА'
    # Способ создания объекта (конструктор)
    def __init__(self):
        pass