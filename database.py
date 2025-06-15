from pymongo import MongoClient
from config import MONGO_URI

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.ikman_tracker
        self.users = self.db.users

    def add_user(self, user_id):
        """Adds a new user to the database."""
        if not self.users.find_one({"_id": user_id}):
            self.users.insert_one({"_id": user_id, "keywords": [], "seen_ads": []})

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
        """Returns a list of all unique keywords subscribed to by users."""
        return self.users.distinct("keywords")

    def get_users_for_keyword(self, keyword):
        """Gets all user IDs subscribed to a specific keyword."""
        users = self.users.find({"keywords": keyword.lower()}, {"_id": 1})
        return [user["_id"] for user in users]

    def has_user_seen_ad(self, user_id, ad_id):
        """Checks if a user has already seen a specific ad."""
        user = self.users.find_one({"_id": user_id, "seen_ads": ad_id})
        return user is not None

    def add_seen_ad_for_user(self, user_id, ad_id):
        """Adds a seen ad to a user's record."""
        self.users.update_one(
            {"_id": user_id},
            {"$addToSet": {"seen_ads": ad_id}}
        )
