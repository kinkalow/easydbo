class EASYDBO_BASE_ERROR(Exception):
    def __init__(self, prompt, message):
        self.prompt = prompt
        self.message = message

    def __str__(self):
        if not self.message:
            return ''
        if isinstance(self.message, str):
            ms = self.message.split('\n')
        ms[0] = f'{self.prompt} {ms[0]}'
        for i in range(1, len(ms)):
            ms[i] = ' ' * (len(self.prompt) + 1) + ms[i]
        return '\n'.join(ms)

class EASYDBO_GOTO_LOOP(EASYDBO_BASE_ERROR):
    def __init__(self, message=''):
        super().__init__('[ERROR]', message)

class EASYDBO_FATAL_ERROR(EASYDBO_BASE_ERROR):
    def __init__(self, message=''):
        super().__init__('[PROGRAM ERROR]', message)

    def __str__(self):
        return '\n' + super().__str__()

class EASYDBO_USER_ERROR(Exception):
    pass
