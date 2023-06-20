import feedparser

from RootSkill import RootSkill

def get_news():
    res=[]
    news_feed = feedparser.parse("http://static.feed.rbc.ru/rbc/logical/footer/news.rss")
    for entry in news_feed.entries:
        desc=entry.get('description', None)
        if desc:
            res.append(desc)
    return res

class News(RootSkill):

    stop_talking = False

    def get_desc(self):
        return "рассказать новости"

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def process(self, command:str)->bool:
        if command in ["новости", "что нового","расскажи новости","какие новости"]:
            count=1
            self.stop_talking = False
            self.say("Новости от РБС:")
            for news in get_news():
                self.say(f"Новость {count}: {news}")
                count+=1

                if self.stop_talking: break
        else:
            return False
        return True

    def stop(self):
        self.stop_talking=True
