from domain.models.user_model import User

""" This function extracts the rolID attribute from a User object and returns it inside a dictionary. """


def user_rolID(user: User) -> dict:
    info_user = {"rolID": user.rolID}
    return info_user
