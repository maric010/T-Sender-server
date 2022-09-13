from telethon.sync import TelegramClient

my_proxy = {
    'proxy_type': "http",  # (mandatory) protocol to use (see above)
    'addr': "45.149.129.130",  # (mandatory) proxy IP address
    'port': 56626,  # (mandatory) proxy port number
    'username': "11kQzRnT",  # (optional) username if the proxy requires auth
    'password': "KDT5UaKG"
}
client = TelegramClient('test2', 3442047, "cacb39d73070900d11d07fe14a476394",proxy=my_proxy)
client.connect()
