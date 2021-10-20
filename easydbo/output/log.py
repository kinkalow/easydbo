class Log:
    @staticmethod
    def error(msg, traceback=False):
        if isinstance(msg, list) and msg:
            print(f'[Error] {msg[0]}')
            for m in msg[1:]:
                print(f'        {m}')
        elif isinstance(msg, str):
            print(f'[Error] {msg}')
        if traceback:
            import sys
            import traceback
            sys.stdout.flush()
            print('--- Traceback ---')
            traceback.print_exc()
        exit(1)

    @staticmethod
    def info(msg):
        print(msg)
