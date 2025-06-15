from pymongo import MongoClient
from config import MONGO_URI

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.ikman_tracker
        self.users = self.db.users
        self.ads = self.db.ads

    def add_user(self, user_id):
        """Adds a new user to the database."""
        if not self.users.find_one({"_id": user_id}):
            self.users.insert_one({"_id": user_id, "keywords": []})

    def subscribe(self, user_id, keyword):
        """Subscribes a user to a keyword."""
        self.users.update_one(
            {"_id": user_id},
            {"$addToSet": {"keywords": keyword.lower()}}
        )

    def unsubscribe(self, user_id, keyword):
        """Unsubscribes a user from a keyword."""
        self.users.update_one(
            {"_id": user_id},
            {"$pull": {"keywords": keyword.lower()}}
        )

    def get_user_keywords(self, user_id):
        """Gets all keywords for a specific user."""
        user = self.users.find_one({"_id": user_id})
        return user.get("keywords", []) if user else []

    def get_all_subscriptions(self):
        """Returns a set of all unique keywords subscribed to by users."""
        pipeline = [
            {"$unwind": "$keywords"},
            {"$group": {"_id": None, "keywords": {"$addToSet": "$keywords"}}},
        ]
        result = list(self.users.aggregate(pipeline))
        if result:
            return result[0].get('keywords', [])
        return []

    def get_users_for_keyword(self, keyword):
        """Gets all user IDs subscribed to a specific keyword."""
        user_ids = []
        for user in self.users.find({"keywords": keyword.lower()}):
            user_ids.append(user["_id"])
        return user_ids

    def has_seen_ad(self, ad_id):
        """Checks if an ad has already been processed."""
        return self.ads.find_one({"_id": ad_id}) is not None

    def add_seen_ad(self, ad_id):
        """Adds a processed ad to the database."""
        self.ads.insert_one({"_id": ad_id})
