from typing import Dict
from db import contests, participants, invitations


def store_contest(contest):
    return contests.insert(contest)


def get_contest():
    for cont in contests:
        return cont


def store_participant(participant):
    return participants.insert(participant)


def get_participant(user_id):
    return participants.find_one(user_id=user_id)


def store_invitation(invitation: Dict):
    return invitations.insert(invitation)


def get_invitation(inv_user_id):
    return invitations.find_one(inv_user_id=inv_user_id)


def update_invitation(inv_user_id):
    data = dict(inv_user_id=inv_user_id, status=True)
    return invitations.update(data, ['inv_user_id'])


def get_number_invitation(ref_user_id):
    return invitations.count(ref_user_id=ref_user_id, status=True)


def delete_invitation(inv_user_id):
    return invitations.delete(inv_user_id=inv_user_id)