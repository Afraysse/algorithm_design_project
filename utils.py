""" HELPER FUNCTIONS """

################## FOR FRIEND REQUESTS ##########################

from model import Relations, User 
from model import db 

def friends_or_pending(user_a_id, user_b_id):
    """ 
    Check to see if users are already friends and checks if there
    is a pending friend request from user_a and user_b.

    Will give a boolean answer.

    """

    is_friends = db.session.query(Relations).filter(Relations.user_a_id == user_a_id,
                                                    Relations.user_b_id == user_b_id,
                                                    Relations.status == "Accepted").first()

    is_pending = db.session.query(Relations).filter(Relations.user_a_id == user_a_id,
                                                    Relations.user_b_id == user_b_id,
                                                    Relations.status == "Requested").first()

    # will return a boolean based upon querying 
    return is_friends, is_pending

def get_friend_requests(user_id):
    """
    Gets the user's friend requests. Returns users that user received 
    friend requests from. Returns users that user sent friend requests
    to.
    """

    recieved_friend_requests = db.session.query(User).filter(Relations.user_b_id == user_id,
                                                            Relations.status == "Requested").join(Relations,
                                                                                                    Relations.user_b_id == User.user_id).all()

    sent_friend_requests = db.session.query(User).filter(Relations.user_a_id == user_id,
                                                        Relations.status == "Requested").join(Relations,
                                                                                                    Relations.user_b_id ==User.user_id).all()

    return recieved_friend_requests, sent_friend_requests

def get_friends(user_id):
    """ 
    Queries db for user's friends. 
    Just returns the query, not user objects.
    """

    friends = db.session.query(User).filter(Relations.user_a_id == user_id,
                                            Relations.status == "Accepted").join(Relations,
                                                                                    Relations.user_b_id == User.user_id)

    return friends 




