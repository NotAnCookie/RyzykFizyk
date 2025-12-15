from fastapi import APIRouter, HTTPException, Cookie, Response, Body
from schemas.session_dto import *
from mappers.session_mapper import *
from services.session_manager.src.session_manager import SessionManager

def get_session_router(session_manager):
    router = APIRouter(
        prefix="/session",
        tags=["Session Management"]
    )

    @router.post("/create", response_model=SessionResponseDTO)
    async def create_session(dto: CreateSessionDTO, response: Response):
        player = create_session_dto_to_domain(dto)
        session = session_manager.create_session(player, dto.language, dto.category)
        await session_manager.start_session(session.id)

        response.set_cookie(key="session_id", value=str(session.id), httponly=True)
        
        return session_to_initial_question_dto(session)

    @router.post("/next_question", response_model=QuestionDTO)
    async def next_question(session_id: int = Cookie(...)):
        try:
            question = await session_manager.get_next_question(session_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        return question_to_dto(question) if question else None
    
    @router.post("/generate-background")
    async def generate_background_question(session_id: int = Body(..., embed=True)):
        try:
            new_question = await session_manager.generate_background_question(session_id)
            if new_question:
                # Zwracamy DTO, żeby frontend mógł je sobie dodać do listy
                return question_to_dto(new_question)
            raise HTTPException(status_code=500, detail="Generation failed")
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        
    
    @router.post("/verify_answer", response_model=QuestionDTO)
    async def verify_answer(
        dto: PlayerAnswerDTO,         
        session_id: int = Cookie(...)
    ):
        try:
            await session_manager.verify_only(
                session_id=session_id, 
                user_value=dto.value, 
                question_id=dto.question_id
            )
            
            session = session_manager.sessions[session_id]
            
            return session_to_current_question_dto(session)

        except KeyError:
            raise HTTPException(status_code=404, detail="Session or question not found")
        

    @router.post("/submit_answer", response_model=QuestionDTO)
    async def submit_answer(dto: PlayerAnswerDTO, session_id: int = Cookie(...)):
        try:
            session = session_manager.sessions[session_id]
            answer = submit_answer_dto_to_domain(dto, session.player.id)

            await session_manager.submit_answer(session_id, answer)

        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_to_current_question_dto(session)
    
    @router.get("/current_question", response_model=QuestionDTO)
    async def get_current_question(session_id: int = Cookie(...)):
        try:
            session = session_manager.sessions[session_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_to_current_question_dto(session)


    @router.get("/summary", response_model=SessionSummaryDTO)
    async def get_summary(session_id: int = Cookie(...)):
        try:
            session = session_manager.sessions[session_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.state != session.state.SUMMARY:
            raise HTTPException(status_code=400, detail="Session not finished yet")
        
        return session_to_summary_dto(session)

    @router.get("/{session_id}", response_model=SessionResponseDTO)
    async def get_session_state(session_id: int):
        try:
            session = session_manager.sessions[session_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")

        return session_to_response_dto(session)

    @router.post("/end", response_model=SessionResponseDTO)
    async def end_session(session_id: int = Cookie(...)):
        try:
            session = session_manager.end_session(session_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_to_response_dto(session)
    
    return router


