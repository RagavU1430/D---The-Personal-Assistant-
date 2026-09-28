from sqlalchemy.orm import Session

from .models import SystemEvent


class SystemEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, event_type: str, message: str) -> SystemEvent:
        event = SystemEvent(event_type=event_type, message=message)
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event
