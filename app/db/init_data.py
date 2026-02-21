from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Filter
from app.services.filter_presets import FILTER_PRESETS


def seed_filter_presets(db: Session) -> int:
    created = 0

    for preset in FILTER_PRESETS:
        exists = db.scalar(select(Filter.id).where(Filter.name == preset["name"]))
        if exists:
            continue

        db.add(
            Filter(
                name=preset["name"],
                description=preset["description"],
                params=preset["params"],
                is_active=True,
            )
        )
        created += 1

    if created:
        db.commit()

    return created
