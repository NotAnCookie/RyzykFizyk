from services.session_manager.src.session_manager import GameSession
from schemas.session_dto import SessionResponseDTO, QuestionDTO, PlayerAnswerDTO, CreateSessionDTO
from schemas.player import Player
from services.session_manager.src.session_manager import PlayerAnswer
from schemas.session_dto import QuestionDTO, SessionSummaryDTO

def create_session_dto_to_domain(dto: CreateSessionDTO) -> Player:
    return Player(id=dto.player_id, name=dto.player_name, email=dto.player_email)

def question_to_dto(q) -> QuestionDTO:
    return QuestionDTO(
        id=q.id,
        text=q.text,
        trivia=q.trivia,
        sourceUrl=q.sourceUrl
    )

def session_to_current_question_dto(session: GameSession) -> QuestionDTO | None:
    if session.currentQuestion < len(session.questions):
        return question_to_dto(session.questions[session.currentQuestion])
    return None

def session_to_summary_dto(session: GameSession) -> SessionSummaryDTO:
    return SessionSummaryDTO(
        session_id=session.id,
        state=session.state.name,
        total_questions=len(session.questions),
        all_questions=[question_to_dto(q) for q in session.questions],
        all_answers=[
            PlayerAnswerDTO(
                question_id=a.questionId,
                value=a.value
            ) for a in session.answers
        ]
    )


def session_to_response_dto(session: GameSession) -> SessionResponseDTO:
    current_question = None
    if session.currentQuestion < len(session.questions):
        current_question = question_to_dto(session.questions[session.currentQuestion])
    
    all_questions = None
    if session.state == session.state.SUMMARY:
        all_questions = [question_to_dto(q) for q in session.questions]

    return SessionResponseDTO(
        session_id=session.id,
        state=session.state.name,
        current_question_index=session.currentQuestion,
        total_questions=len(session.questions),
        current_question=current_question,
        all_questions=all_questions
    )

# sesja bez pytań
def session_to_initial_question_dto(session: GameSession) -> SessionResponseDTO:
    current_question = None
    if session.currentQuestion < len(session.questions):
        current_question = question_to_dto(session.questions[session.currentQuestion])

    return SessionResponseDTO(
        session_id=session.id,
        state=session.state.name,
        current_question_index=session.currentQuestion,
        total_questions=len(session.questions),
        current_question=current_question,
        all_questions=None  # bez questions
    )

def submit_answer_dto_to_domain(dto: PlayerAnswerDTO, player_id: int) -> PlayerAnswer:
    return PlayerAnswer(
        questionId=dto.question_id,
        playerId=player_id,
        value=dto.value
    )
