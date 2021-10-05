class Log:
    @staticmethod
    def error(msg):
        if isinstance(msg, list) and msg:
            print(f'[Error] {msg[0]}')
            for m in msg[1:]:
                print(f'        {m}')
        elif isinstance(msg, str):
            print(f'[Error] {msg}')
        exit(1)
