import numpy as np
import pandas as pd

class UserProfile:
    def __init__(self, tags_df, names_df):
        self.games = []
                                     
        self.tags_df = tags_df
        self.names_df = names_df[['name', 'median_playtime']]
        
    def add_game(self, gameInfo):
        self.games.append(gameInfo)
        
    def build_profile(self):
        self.names_df['rating'] = float('nan')
        
        # Compute game rating
        
        total_recent = 0
        all_games = []
        for game in self.games:
            total_recent += game.get_recent_hours()
            all_games.append(game.get_app_id())
        
        for game in self.games:
            median = self.names_df.loc[game.get_app_id(), 'median_playtime']
            
            total_weight = 0
            if game.get_total_hours() >= 2:
                total_weight = np.clip(game.get_total_hours() / median, 0, 1) * 0.5
            
            rating_weight = game.get_rating()
            
            recent_weight = 0
            if total_recent > 0:
                recent_weight = game.get_recent_hours() / total_recent
               
            overall_weight = total_weight + rating_weight + recent_weight
            
            self.names_df.loc[game.get_app_id(), 'rating'] = overall_weight
        
        # Normalize ratings
        
        ratings_filter = self.names_df['rating'].notna()
        ratings_mean = self.names_df.loc[ratings_filter, 'rating'].mean()
        self.names_df.loc[ratings_filter, 'rating'] = self.names_df.loc[ratings_filter, 'rating'].sub(ratings_mean)
        
        # Build actual model
        
        # Tags are the columns
        # Games are the rows
        
        game_ratings = self.names_df.loc[all_games, 'rating']
        game_tags = self.tags_df.loc[all_games]
        
        tag_sums = game_tags.sum(axis=1)
        tag_mults = game_tags.mul(game_ratings, axis=0)
        
        self.model = tag_mults.div(tag_sums, axis=0).sum()
        
    def recommend(self, n=10):
        exclude_games = []
        for game in self.games:
            exclude_games.append(game.get_app_id())
            
        tags = self.tags_df.drop(exclude_games, axis=0)
        
        top = tags.mul(self.model, axis=1).sum(axis=1)
        tags_len = np.sqrt((tags * tags).sum(axis=1))
        model_len = np.sqrt((self.model * self.model).sum())
        
        cos = top / (tags_len * model_len)
        cos = cos.nlargest(n)
        
        indices = cos.index
        
        cos_frame = cos.to_frame()
        cos_frame['name'] = self.names_df.loc[indices, 'name']
        
        return (indices, cos_frame)
    