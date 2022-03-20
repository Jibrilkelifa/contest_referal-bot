from email import message
from typing import Dict
from db import contests, participants, invitations
from constants import NOT_STARTED_YET


def store_contest(contest):
    contest['status'] = NOT_STARTED_YET
    return contests.insert(contest)


def delete_contest():
    return contests.delete()


def update_contest(id, value):
    data = dict(id=id, status=value)
    return contests.update(data, ['id'])


def update_contest_message_id(id, value):
    data = dict(id=id, message_id=value)
    return contests.update(data, ['id'])


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


def get_total_participant():
    return len(participants)


def get_total_invitation():
    return invitations.count(status=True)


def truncate_all_tables():
    contests.delete()
    participants.delete()
    invitations.delete()


def award():
    #zero participant
    if (not get_total_participant()):
        return []
    else:
        l = []
        for participant in participants:
            total_num_inv = get_number_invitation(participant['user_id'])
            tu = (participant, total_num_inv)
            l.append(tu)
        l.sort(reverse=True, key=lambda x: x[1])
        return l


def get_rank(participant_id):
    total_participant = get_total_participant()
    l = []
    for participant in participants:
        total_num_inv = get_number_invitation(participant['user_id'])
        tu = (participant['user_id'], total_num_inv)
        l.append(tu)
    l.sort(reverse=True, key=lambda x: x[1])
    result = [l.index(i) + 1 for i in l if i[0] == participant_id][0]
    return f"📊You rank {result} out of {total_participant} participant(s)"
