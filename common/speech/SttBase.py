class SttBase:
    _force_stop = [False]
    _logger = None
    keywords = []

    def __init__(self, logger, keywords=None):
        self._logger=logger
        self.keywords=keywords
        if logger:
            logger.info(f"{self.__class__.__name__} initing ...")

    def recognize_wav(self, wav_filename:str, samplerate):
        """recognize wav file"""
        pass

    def recognize(self, voice_required_try=None, noise_detect_len=None):
        """recognize and wait for keyword"""
        pass

    def wait_for_keyword(self):
        while not self.is_force_stop():
            text = self.recognize()
            if text :
                for word in text.split():
                    if word in self.keywords:
                        return text.replace(word,'').strip()
        return ""

    def is_force_stop(self):
        return self._force_stop[0]

    def force_stop(self):
        self._force_stop = [True]