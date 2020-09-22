class Game:
    def __init__(self, appid, rating, hours_total, hours_recent):
        self.appid = appid
        self.rating = rating
        self.hours_total = hours_total
        self.hours_recent = hours_recent
    
    def get_app_id(self):
        return self.appid
    
    def get_rating(self):
        return self.rating
    
    def get_total_hours(self):
        return self.hours_total
    
    def get_recent_hours(self):
        return self.hours_recent
