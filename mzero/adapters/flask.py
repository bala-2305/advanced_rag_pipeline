"""Flask integration adapter for mzero."""

from typing import Any
from mzero.main import RAG


def create_mzero_blueprint(rag_instance: RAG, name: str = "mzero", url_prefix: str = "/rag"):
    """Creates a Flask Blueprint for embedding mzero in existing Flask applications."""
    try:
        from flask import Blueprint, request, jsonify
    except ImportError:
        raise ImportError("Flask is required to use create_mzero_blueprint. Install with: pip install flask")

    bp = Blueprint(name, __name__, url_prefix=url_prefix)

    @bp.route("/ask", methods=["POST"])
    def ask():
        data = request.get_json(force=True) or {}
        question = data.get("question", "")
        cid = data.get("conversation_id")
        res = rag_instance.ask(question, conversation_id=cid)
        return jsonify(res.model_dump())

    @bp.route("/stats", methods=["GET"])
    def stats():
        return jsonify(rag_instance.stats().model_dump())

    return bp
