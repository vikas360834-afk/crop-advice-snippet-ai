"""Farmer Feedback and Rating Module.

Enables farmers to rate generated advice snippets:
- 1 to 5 star rating
- Advice ID or crop reference
- Problem addressed
- Free-form comments
- Whether recommendation was practical / useful
- Date of feedback
- Generates feedback analytics and maintains separation between
  unverified user feedback and verified training corpus.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_FEEDBACK_PATH = Path("data/farmer_feedback.jsonl")


class FarmerFeedback:
    def __init__(
        self,
        id: str,
        crop: str,
        rating: int,
        advice_id: str = "",
        problem: str = "",
        comment: str = "",
        was_useful: bool = True,
        date: str = "",
    ):
        self.id = str(id).strip()
        self.crop = str(crop).strip().title()
        self.rating = int(rating)
        if not (1 <= self.rating <= 5):
            raise ValueError(f"Rating must be between 1 and 5 (got {self.rating}).")
        self.advice_id = str(advice_id).strip()
        self.problem = str(problem).strip()
        self.comment = str(comment).strip()
        self.was_useful = bool(was_useful)
        self.date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "crop": self.crop,
            "rating": self.rating,
            "advice_id": self.advice_id,
            "problem": self.problem,
            "comment": self.comment,
            "was_useful": self.was_useful,
            "date": self.date,
        }


class FeedbackManager:
    def __init__(self, path: Path | str = DEFAULT_FEEDBACK_PATH):
        self.path = Path(path)
        self.feedback_list: List[FarmerFeedback] = []
        self.load()

    def load(self) -> None:
        self.feedback_list = []
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                self.feedback_list.append(FarmerFeedback(**data))
            except Exception:
                pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(f.to_dict()) for f in self.feedback_list]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add(self, feedback: FarmerFeedback) -> None:
        self.feedback_list.append(feedback)
        self.save()

    def get_analytics(self) -> Dict[str, Any]:
        if not self.feedback_list:
            return {
                "total_ratings": 0,
                "average_rating": 0.0,
                "rating_distribution": {str(k): 0 for k in range(1, 6)},
                "usefulness_rate": "0%",
            }

        total = len(self.feedback_list)
        avg = sum(f.rating for f in self.feedback_list) / total
        dist = {str(k): 0 for k in range(1, 6)}
        useful_count = sum(1 for f in self.feedback_list if f.was_useful)

        for f in self.feedback_list:
            dist[str(f.rating)] += 1

        return {
            "total_ratings": total,
            "average_rating": round(avg, 2),
            "rating_distribution": dist,
            "useful_count": useful_count,
            "usefulness_rate": f"{round((useful_count / total) * 100, 1)}%",
        }
