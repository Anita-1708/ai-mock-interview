prompt = """You are observing a live technical coding interview. The conversation has included a sequence of interactions between the candidate and the interviewer.
The candidate has just unmuted their microphone and spoken aloud. Your task is to determine whether the candidate is asking for a hint related to the coding problem they are solving.
Use the full context of the interaction, including the message history below and the candidate’s latest spoken utterance, to make your decision.

Assistant is basically what agent has said and user is what user has said till now
Message History:
[{messages}]


Instructions:
Analyze the spoken input in the context of the full conversation. Focus on:
Expressions of confusion, hesitation, or uncertainty.
Indirect or direct requests for help or guidance.
Phrases like: “Am I on the right track?”, “What should I do next?”, “Is this okay?”, “I'm stuck,” etc.
Requests for confirmation or validation of approach.
Respond with:
"COMPLETE" — if the candidate is likely asking for a hint.
"NOT_COMPLETE" — if the candidate is not asking for a hint."""