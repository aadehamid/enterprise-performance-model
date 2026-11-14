import math

from fastapi import HTTPException, Request

from app.api.question import Question


def clean_nans(val):
    if isinstance(val, float) and math.isnan(val):
        return None
    elif isinstance(val, dict):
        return {k: clean_nans(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [clean_nans(item) for item in val]
    elif isinstance(val, tuple):
        return tuple(clean_nans(item) for item in val)
    return val


class Routes:

    def __init__(self, app, agent, message_history, allowed_origins):
        self._app = app
        self._agent = agent
        self._message_history = message_history
        self._allowed_origins = allowed_origins
        self._register_routes()

    def _register_routes(self):
        @self._app.post("/ask")
        def ask_question(request: Request, question: Question):
            try:
                referer = request.headers.get("referer", "")
                if not any(allowed in referer for allowed in self._allowed_origins):
                    raise HTTPException(status_code=403, detail="Forbidden: Invalid referrer")

                history, _, current_session_id = self._message_history.create_history(session_id=question.session_id)

                input = (question.question or "").strip()
                print(f"User Question: {input}")

                prior_turns = history.messages
                history.add_message({"role": "user", "content": input})
                answer = self._agent.ask(input, prior_turns)
                history.add_message({"role": "assistant", "content": answer.text})

                self._message_history.record_message(
                    session_id=current_session_id,
                    question=input,
                    cypher=answer.cypher,
                    answer=answer.text
                )

                return clean_nans({
                    "response": answer.text,
                    "cypher": answer.cypher,
                    "error": answer.error,
                    "src": [{
                        "listIds": answer.element_ids,
                        "rows": answer.rows,
                        "graph_data": answer.graph,
                        "headers": answer.headers,
                    }],
                    "session_id": current_session_id,
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self._app.post("/api/expand")
        def expand_node(request: Request, data: dict):
            """1-hop neighbourhood of a node. Body: { 'element_id': '...' }"""
            eid = data.get("element_id")
            if not eid:
                raise HTTPException(status_code=400, detail="Missing element_id parameter.")
            try:
                return self._agent.expand(eid)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self._app.post("/api/feedback")
        def submit_feedback(request: Request, data: dict):
            """Body: { 'session_id': '...', 'feedback': 'good'|'poor', 'comment': '...' }"""
            session_id = data.get("session_id")
            feedback = data.get("feedback")
            comment = data.get("comment", "")
            if not session_id or not feedback:
                raise HTTPException(status_code=400, detail="Missing session_id or feedback parameter.")
            try:
                self._message_history.submit_feedback(session_id, feedback, comment)
                return {"status": "success", "message": "Feedback submitted successfully."}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
