#Actionableitems , decision , questions 

from core.analysis import analyse_transcript

def extract_action_items(transcript:str)->str:
    return analyse_transcript(transcript)["action_items"]


def extract_key_decisions(transcript: str) -> str:
    return analyse_transcript(transcript)["key_decisions"]


def extract_questions(transcript: str) -> str:
    return analyse_transcript(transcript)["open_questions"]
