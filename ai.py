import logging
from typing import TypedDict
import json
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langgraph.graph import StateGraph
from question_service import QuestionService

from data_class import MessageRequest
from enums import Phase
from memory.session import create_session, add_message, get_session, update_phase, flatten_message_history, \
    flatten_message_history_based_on_phase
from sop_prompts import intent_analysis, intro_message_prompt

load_dotenv()

class ProcessingState(TypedDict):
    input: str
    output: str
    phase: Phase
    request_id: str
    step: int
    perspective_analysis: str



def start_new_interview():
    phase  = Phase.INTRO_PHASE
    session_id  = create_session()
    workflow = StateGraph(ProcessingState)
    workflow.add_node("intro_phase", intro_phase_node)
    workflow.set_entry_point("intro_phase")

    chain = workflow.compile()
    result = chain.invoke({
        "input": "",
        "output": "",
        "phase": Phase.START,
        "request_id": session_id
    })

    add_message(session_id,"assistant",result["output"],phase)
    update_phase(session_id=session_id, phase=phase)

    session_dat = get_session(session_id)
    print(session_dat)
    result["session_id"] = session_id
    return result


logger = logging.getLogger(__name__)





def start_phase(state: ProcessingState) -> ProcessingState:

    request_id = state["request_id"]
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1, max_tokens=5000)
    combined_input = f""""""
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(intent_analysis),
        ])
    )
    logger.warning(f"{request_id} - Processing start_phase step")
    state["output"] = chain.run(input=combined_input)  # Use combined input
    state["phase"] = Phase.INTRO_PHASE
    state["step"] = 3
    return state


def intro_intent_analysis_node(state: ProcessingState) -> ProcessingState:
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing intent_analysis_node step")
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1, max_tokens=2048)
    session = get_session(session_id=request_id)
    messages = flatten_message_history(session['message_history'])


    print(session)

    combined_input = f"""You are an intelligent interview assistant managing an interview with a candidate. The interview process has 6 phases defined below:

class Phase(Enum):
    START = 1
    INTRO_PHASE = 2
    QUESTION_PHASE = 3
    APPROACH_PHASE = 4
    CODING_PHASE = 5
    EVALUATION_PHASE = 6
Each user response belongs to one of the above phases. Your job is:

Analyze the user’s latest response.

Current Phase : {state['phase']}

Decide whether the phase is complete.

If complete, return COMPLETE

If not complete, return NOT_COMPLETE

Definitions:
START: The user has just joined. No introduction yet.

INTRO_PHASE: The user introduces.

QUESTION_PHASE: The interviewer explain the question

APPROACH_PHASE: The user explains their approach to solving a coding or system design problem.

CODING_PHASE: The user writes or describes code/logic in detail.

EVALUATION_PHASE: The interviewer asks follow-ups, evaluates reasoning, discusses improvements or edge cases.

Assistant is basically what agent has said and user is what user has said


Message History : [{messages} ]"
reply with enum only strictly. [COMPLETE, NOT_COMPLETE]
"""

    print("====")


    print(combined_input)

    print("====")
    print(state['input'])
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(combined_input),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    logger.warning(f"{request_id} - Processing intent_analysis_node step")

    state["output"] = chain.run(input=state['input'])

    logger.warning(f"{request_id} - Processing intent_analysis_node step")
    print(state["output"])

    # state["phase"] = Phase.INTRO_PHASE
    state["step"] = 3
    return state

def intent_analysis_classify(state : ProcessingState) -> str:

    if(state["output"] == "COMPLETE"):
        return "complete"
    else:
        return "not_complete"


def ask_follow_up_node(state : ProcessingState) -> ProcessingState:
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing ask_follow_up_node step")
    llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=1, max_tokens=5000)
    session = get_session(session_id=request_id)
    messages = flatten_message_history_based_on_phase(session['message_history'],state['phase'])

    prompt = f"""You are conducting an ongoing interview that progresses through six structured phases.

Current Phase: {state['phase']}

Here is the conversation history so far:

[{messages} ]
Based on this message history, ask the next follow-up question in a natural, conversational tone appropriate to the current phase of the interview on a call.

Ensure your question:

Feels human and engaging

Builds smoothly on what the candidate has already shared

Is appropriate for the {state['phase']} stage of the interview

Do not repeat previously asked questions or summarize the history — simply continue the flow of the conversation naturally."""



    print(prompt)

    print("====")
    print(state['input'])
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompt),
            # HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    add_message(request_id,"user",state["input"] ,state["phase"])

    logger.warning(f"{request_id} - Processing ask_follow_up_node step")
    state["output"] = chain.run(input="")
    logger.warning(f"{request_id} - Processing ask_follow_up_node step")
    print(state["output"])
    # state["phase"] = Phase.INTRO_PHASE
    state["step"] = 3
    add_message(request_id,"assistant",state["output"] ,state["phase"])

    return state


def approach_intent_analysis(state : ProcessingState) -> ProcessingState:
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing ask_follow_up_node step")
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1, max_tokens=2048)
    session = get_session(session_id=request_id)

    messages = flatten_message_history_based_on_phase(session['message_history'],session['phase'])


    prompt = f"""You are a DSA interview assistant conducting the APPROACH PHASE of a coding interview.

The student is attempting to explain their approach for the following question:

Question: [You are given an even-length array nums of integers and a positive integer limit. Consider each pair formed by elements at positions i and 2n - 1 - i, where n = len(nums) // 2. Your goal is to make the sum of every such pair equal to the same target value. To achieve this, you are allowed to perform at most one operation on each pair: replace both elements with any integers between 1 and limit (inclusive). Return the minimum number of operations needed to make all pairs sum to the same value. For example, given nums = [1, 2, 4, 3] and limit = 4, the pairs are (1, 3) and (2, 4), which sum to 4 and 6 respectively. Changing (2, 4) to (2, 2) makes both pairs sum to 4 using just one operation. Your task is to determine the optimal target sum and count the minimal operations needed across all pairs. The input constraints are: 2 <= len(nums) <= 10^5, len(nums) is even, and 1 <= nums[i], limit <= 10^5.]


Below is the message history between the student and the assistant so far:
[{messages}]

In this phase, your job is to evaluate the **most recent answer provided by the student**, which comes next as a human message.

Evaluation Criteria:
- The approach must be relevant to the given question.
- It should clearly outline the steps or strategy the student intends to take to solve the problem.
- It should demonstrate logical clarity, feasibility, and awareness of key edge cases.
- If this is a follow-up attempt (i.e., previous answers were incomplete), the new response should fix earlier gaps or add meaningful improvements.

You MUST respond with one of the following **strict values only**:
- `COMPLETE` → if the student's latest approach is clearly explained and acceptable.
- `NOT_COMPLETE` → if the latest explanation is incorrect, vague, or incomplete.

Do not add any extra explanation or reasoning. Just respond with `COMPLETE` or `NOT_COMPLETE`."""

    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompt),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    logger.warning(f"{request_id} - Processing approach_intent_analysis step")
    state["output"] = chain.run(input=state['input'])

    logger.warning(f"{request_id} - Processing approach_intent_analysis step")
    print(state["output"])
    # state["phase"] = Phase.INTRO_PHASE
    state["step"] = 4
    return state






def route_to_phase(state : ProcessingState) -> str:

    session = get_session(session_id=state["request_id"])

    if(session["phase"] == Phase.INTRO_PHASE):
        return "intro_phase"
    elif(session["phase"] == Phase.APPROACH_PHASE):
        return "approach_phase"
    elif(session["phase"] == Phase.CODING_PHASE):
        return "coding_phase"

    return "invalid"

def step_to_phase(state : ProcessingState) -> ProcessingState:
    return state


def processRequest(user_input: str,session_id : str) -> str:
    """
    Process interview request with phase-based workflow
    """
    workflow = StateGraph(ProcessingState)
    
    # Add interview phase nodes
    workflow.add_node("intro_phase", intro_phase_node)
    workflow.add_node("start_phase", start_phase)
    workflow.add_node("question_phase", question_phase_node)
    workflow.add_node("approach_phase", approach_phase_node)
    workflow.add_node("coding_phase", coding_phase_node)
    workflow.add_node("evaluation_phase", evaluation_phase_node)
    workflow.add_node("end_interview", end_interview_node)
    workflow.add_node("phase_rout", phase_dummy)
    workflow.add_node("intro_intent_analysis", intro_intent_analysis_node)
    workflow.add_node("ask_follow_up",ask_follow_up_node)
    workflow.add_node("step_to_phase",step_to_phase)
    workflow.add_node("approach_intent_analysis",approach_intent_analysis)
    
    workflow.set_entry_point("step_to_phase")


    workflow.add_conditional_edges(
        "step_to_phase",
        route_to_phase,
        {
            "intro_phase":"intro_intent_analysis",
            "approach_phase":"approach_intent_analysis",
            # "coding_phase":"coding_phase",
        }
    )



    workflow.add_conditional_edges(
        "intro_intent_analysis",
        intent_analysis_classify,
        {
            "complete":"question_phase",
            "not_complete":"ask_follow_up"
        }

    )

    workflow.add_conditional_edges(
        "approach_intent_analysis",
        intent_analysis_classify,
        {
            "complete":"evaluation_phase",
            "not_complete":"ask_follow_up"
        }

    )


    # workflow.add_conditional_edges(
    #     "phase_rout",
    #     phase_router,
    #     {
    #         "start_phase": "start_phase",
    #         "intent_analysis" :"intent_analysis"
    #     }
    # )

    workflow.add_conditional_edges(
        "intro_phase",
        phase_router,
        {
            "question_phase": "question_phase",
            "end_interview": "end_interview"
        }
    )

    # workflow.add_conditional_edges(
    #     "question_phase",
    #     phase_router,
    #     {
    #         "approach_phase": "approach_phase",
    #         "end_interview": "end_interview"
    #     }
    # )

    workflow.add_conditional_edges(
        "approach_phase",
        phase_router,
        {
            "coding_phase": "coding_phase",
            "end_interview": "end_interview"
        }
    )

    workflow.add_conditional_edges(
        "coding_phase",
        phase_router,
        {
            "evaluation_phase": "evaluation_phase",
            "end_interview": "end_interview"
        }
    )

    # workflow.add_conditional_edges(
    #     "evaluation_phase",
    #     phase_router,
    #     {
    #         "end_interview": "end_interview"
    #     }
    # )
    
    # Compile and run
    chain = workflow.compile()
    result = chain.invoke({
        "input": user_input,
        "output": "",
        "phase": Phase.START,
        "request_id": session_id
    })
    
    return result["output"]


def processInterviewPhase(user_input: str, target_phase: Phase, request_id: str = None) -> str:
    """
    Process interview for a specific phase
    """
    workflow = StateGraph(ProcessingState)

    # Add interview phase nodes
    workflow.add_node("intro_phase", intro_phase_node)
    workflow.add_node("question_phase", question_phase_node)
    workflow.add_node("approach_phase", approach_phase_node)
    workflow.add_node("coding_phase", coding_phase_node)
    workflow.add_node("evaluation_phase", evaluation_phase_node)
    workflow.add_node("end_interview", end_interview_node)

    # Set entry point based on target phase
    if target_phase == Phase.INTRO_PHASE:
        workflow.set_entry_point("intro_phase")
    elif target_phase == Phase.QUESTION_PHASE:
        workflow.set_entry_point("question_phase")
    elif target_phase == Phase.APPROACH_PHASE:
        workflow.set_entry_point("approach_phase")
    elif target_phase == Phase.CODING_PHASE:
        workflow.set_entry_point("coding_phase")
    elif target_phase == Phase.EVALUATION_PHASE:
        workflow.set_entry_point("evaluation_phase")
    else:
        workflow.set_entry_point("end_interview")

    # Add direct edges to end for single-phase processing
    workflow.add_edge("intro_phase", "end_interview")
    workflow.add_edge("question_phase", "end_interview")
    workflow.add_edge("approach_phase", "end_interview")
    workflow.add_edge("coding_phase", "end_interview")
    workflow.add_edge("evaluation_phase", "end_interview")

    # Compile and run
    chain = workflow.compile()
    result = chain.invoke({
        "input": user_input,
        "output": "",
        "phase": target_phase,
        "request_id": request_id or f"interview_{hash(user_input)}",
        "step": 0,
        "course_data": "",
        "humanizer_model": "",
        "sop_generation_version": "",
        "needs_rewrite": False,
        "ai_retry_count": 0,
        "wc": 0,
        "issues_output": "",
        "needs_first_person": False,
        "for_humanize": "",
        "perspective_analysis": ""
    })

    return result["output"]


def getPhaseDescription(phase: Phase) -> str:
    """
    Get description of each interview phase
    """
    descriptions = {
        Phase.START: "Interview initialization",
        Phase.INTRO_PHASE: "Introduction and welcome phase",
        Phase.QUESTION_PHASE: "Technical and behavioral questions",
        Phase.APPROACH_PHASE: "Problem-solving approach discussion",
        Phase.CODING_PHASE: "Coding challenge and implementation",
        Phase.EVALUATION_PHASE: "Feedback and evaluation"
    }
    return descriptions.get(phase, "Unknown phase")


# class InterviewSession:
#     """
#     Class to manage interview session state and flow
#     """
#
#     def __init__(self, session_id: str = None):
#         self.session_id = session_id or f"session_{hash(str(id(self)))}"
#         self.current_phase = Phase.START
#         self.phase_history = []
#         self.user_responses = []
#         self.interviewer_responses = []
#         self.session_started = False
#
#     # def start_interview(self, user_input: str) -> str:
#     #     """
#     #     Start the interview session
#     #     """
#     #     self.session_started = True
#     #     self.current_phase = Phase.INTRO_PHASE
#     #     return self.process_phase(user_input)
#
#     def process_phase(self, user_input: str) -> str:
#         """
#         Process the current phase with user input
#         """
#         self.user_responses.append(user_input)
#         self.phase_history.append(self.current_phase)
#
#         # Process the current phase
#         response = processInterviewPhase(user_input, self.current_phase, self.session_id)
#         self.interviewer_responses.append(response)
#
#         return response
#
#     # def next_phase(self, user_input: str = "") -> str:
#     #     """
#     #     Move to the next phase
#     #     """
#     #     self.current_phase = getNextPhase(self.current_phase)
#     #     return self.process_phase(user_input)
#     #
#     # def go_to_phase(self, target_phase: Phase, user_input: str = "") -> str:
#     #     """
#     #     Jump to a specific phase
#     #     """
#     #     self.current_phase = target_phase
#     #     return self.process_phase(user_input)
#     #
#     # def get_session_summary(self) -> dict:
#     #     """
#     #     Get summary of the interview session
#     #     """
#     #     return {
#     #         "session_id": self.session_id,
#     #         "current_phase": self.current_phase,
#     #         "phase_description": getPhaseDescription(self.current_phase),
#     #         "total_phases_completed": len(self.phase_history),
#     #         "session_started": self.session_started,
#     #         "phase_history": [getPhaseDescription(phase) for phase in self.phase_history]
#     #     }
#     #
#     # def is_completed(self) -> bool:
#     #     """
#     #     Check if interview is completed
#     #     """
#     #     return self.current_phase == Phase.EVALUATION_PHASE and len(self.phase_history) > 0


# Example usage functions
def run_complete_interview(user_input: str) -> str:
    """
    Run a complete interview flow from start to finish
    """
    return processRequest(user_input)


def run_interview_phase(user_input: str, phase: Phase) -> str:
    """
    Run a specific interview phase
    """
    return processInterviewPhase(user_input, phase)


# def create_interview_session() -> InterviewSession:
#     """
#     Create a new interview session
#     """
#     return InterviewSession()


# Example usage:
# if __name__ == "__main__":



# Interview Phase Nodes
def intro_phase_node(state: ProcessingState) -> ProcessingState:
    """
    Node for interview introduction phase
    """
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing intro phase")


    llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.7, max_tokens=2000)
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(intro_message_prompt),
        ])
    )

    state["output"] = chain.run(input=state["input"])
    # state["phase"] = Phase.INTRO_PHASE
    # state["step"] = 1
    return state


def question_phase_node(state: ProcessingState) -> ProcessingState:
    """
    Node for interview question phase
    """
    request_id = state["request_id"]
    session = get_session(session_id=request_id)
    service = QuestionService(openai_api_key="your_api_key")
    question =  service.generate_question()
    session['question'] = question
    logger.warning(f"{request_id} - Processing question phase")
    
    llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0.8, max_tokens=2000)


    prompt = f"""You are a technical interviewer bot conducting coding interviews in a conversational and interactive manner. Your goal is to assess the candidate's problem-solving ability by guiding them through algorithmic challenges.

You do not simply read out the question. Instead, you explain the problem context clearly and naturally, helping the candidate understand the scenario before they begin solving it.

When the interview starts, greet the candidate professionally and introduce the problem in a step-by-step way, using conversational phrasing. Encourage the candidate to think aloud and clarify if they have questions. Always maintain a professional and supportive tone.

You will be provided with a coding problem description as input. Use this to frame your explanation and kick off the interview.

Begin by saying something like:

"Let’s begin the interview. I’ll walk you through the problem first, and then we’ll dive into your approach."


Then, explain the problem using the provided description—engagingly and clearly—not just reading it out word-for-word.

question : [{question}]

Your role is not to solve the problem but to guide, clarify, and evaluate.

"""


    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompt),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    add_message(request_id,"user",state["input"],state["phase"])
    state["output"] = chain.run(input=state["input"])
    state["phase"] = Phase.APPROACH_PHASE
    state["step"] = 2
    add_message(request_id,"assistant",state["output"] ,state["phase"])
    update_phase(request_id, Phase.APPROACH_PHASE)

    return state


def approach_phase_node(state: ProcessingState) -> ProcessingState:
    """
    Node for interview approach phase
    """
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing approach phase")
    
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7, max_tokens=2000)
    
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are an AI interviewer in the approach phase. 
Based on the candidate's responses, you should:
1. Present a technical problem or scenario
2. Ask them to explain their approach to solving it
3. Encourage them to think out loud
4. Ask follow-up questions about their reasoning
5. Assess their analytical thinking

Present a challenging but fair technical problem and guide them through their approach."""),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    
    state["output"] = chain.run(input=state["input"])
    state["phase"] = Phase.APPROACH_PHASE
    state["step"] = 3
    return state


def coding_phase_node(state: ProcessingState) -> ProcessingState:
    """
    Node for interview coding phase
    """
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing coding phase")
    
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.6, max_tokens=2000)
    
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are an AI interviewer in the coding phase. 
You should:
1. Present a coding challenge appropriate to their skill level
2. Ask them to write code or pseudocode
3. Discuss their implementation approach
4. Ask about time and space complexity
5. Provide hints if they get stuck
6. Evaluate their coding style and problem-solving

Present a coding problem that tests their technical skills and coding abilities."""),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    
    state["output"] = chain.run(input=state["input"])
    state["phase"] = Phase.CODING_PHASE
    state["step"] = 4
    return state


def evaluation_phase_node(state: ProcessingState) -> ProcessingState:
    """
    Node for interview evaluation phase
    """
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Processing evaluation phase")
    
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5, max_tokens=2000)
    
    chain = LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are an AI interviewer in the evaluation phase. 
You should:
1. Thank the candidate for their time
2. Provide constructive feedback on their performance
3. Highlight their strengths
4. Mention areas for improvement
5. Ask if they have any questions
6. End the interview professionally

Provide a balanced evaluation of their interview performance."""),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )
    
    state["output"] = chain.run(input=state["input"])
    state["phase"] = Phase.EVALUATION_PHASE
    state["step"] = 5
    return state


def phase_dummy(state: ProcessingState) -> ProcessingState:
    return state


def phase_router(state: ProcessingState) -> str:
    """
    Router function to determine which phase to go to next
    """
    request_id = state["request_id"]
    current_phase = state.get("phase", Phase.START)
    user_input = state.get("input", "").lower()
    
    logger.warning(f"{request_id} - Current phase: {current_phase}")
    logger.warning(f"{request_id} - User input: {user_input}")
    # Default phase progression

    if state.get("input") == '/start':
        return "start_phase"

    else:
        return "intent_analysis"


def end_interview_node(state: ProcessingState) -> ProcessingState:
    """
    Node to end the interview
    """
    request_id = state["request_id"]
    logger.warning(f"{request_id} - Interview completed")
    
    state["output"] = "Interview session completed. Thank you for participating!"
    state["step"] = 6
    return state
