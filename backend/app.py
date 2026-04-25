"""Flask application — exposes the AI agent pipeline as a REST API."""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from pipeline.orchestrator import Orchestrator

app = Flask(__name__)
CORS(app)

DEFAULT_FORMATS = ["book", "journal", "comic"]


@app.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.route("/search", methods=["POST"])
def search() -> tuple:
    """Run the AI pipeline and return the top 3 books.

    Expects JSON body::

        {
            "query": "natural language search",
            "formats": ["book", "comic"]   // optional
        }
    """
    body = request.get_json(silent=True) or {}
    query = body.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    formats: list[str] = body.get("formats") or DEFAULT_FORMATS

    try:
        orchestrator = Orchestrator()
        result = orchestrator.run(query, formats)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
