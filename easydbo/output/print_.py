class SimplePrint:
    @staticmethod
    def debug(msg):
        print(f'[DEBUG] {msg}')

    @staticmethod
    def error(msg, traceback=False, do_exit=True):
        if isinstance(msg, list) and msg:
            print(f'[ERROR] {msg[0]}')
            for m in msg[1:]:
                print(f'        {m}')
        elif isinstance(msg, str):
            print(f'[ERROR] {msg}')
        if traceback:
            import sys
            import traceback
            sys.stdout.flush()
            print('--- Traceback ---')
            traceback.print_exc()
        if do_exit:
            exit(1)

    @staticmethod
    def fatal_error(msg):
        print(f'[FATAL ERROR] {msg}')
        exit(1)

    @staticmethod
    def info(msg):
        print(f'[INFO] {msg}')

    @staticmethod
    def miss(msg):
        print(f'[MISS] {msg}')

    @staticmethod
    def output(msg):
        print(msg)
