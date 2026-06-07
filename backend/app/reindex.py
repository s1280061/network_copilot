"""Manual RAG reindex: python -m app.reindex [--force]"""
import sys

from .services.rag import reindex

if __name__ == "__main__":
    force = "--force" in sys.argv
    report = reindex(force=force)
    print(report)
