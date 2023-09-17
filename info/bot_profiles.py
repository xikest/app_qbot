from collections import namedtuple

profile = namedtuple(typename='profiles', field_names=['TOKEN', 'channels'])


class BotProfiles:
    @staticmethod
    def get_botBeta():
        return profile(TOKEN='5419434216:AAGf88KSC0ETWkSkogbf3N7pmzcQEG0PAQ8',
                       channels={'beta_chat_id': '-1001601197449'})

