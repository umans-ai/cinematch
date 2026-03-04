"""
Persistence integration tests for Room entity.

Pattern: given [precondition] when [action] then [expected outcome]
"""

import pytest
from sqlalchemy.orm import Session

from app.models import Room


class TestRoomRepository:
    """Test suite for Room persistence operations."""

    def test_given_no_rooms_when_query_all_then_returns_empty_list(self, db_session: Session):
        """given: no rooms exist when: query all rooms then: returns empty list"""
        rooms = db_session.query(Room).all()
        assert rooms == []

    def test_given_room_saved_when_get_by_id_then_retrieved_matches_saved(self, db_session: Session):
        """
        given: room is saved to database
        when: retrieve room by id
        then: retrieved room matches saved room
        """
        # given
        room = Room(code="1234", is_active=True)
        db_session.add(room)
        db_session.commit()
        db_session.refresh(room)

        # when
        retrieved = db_session.query(Room).filter_by(id=room.id).first()

        # then
        assert retrieved is not None
        assert retrieved.code == "1234"
        assert retrieved.is_active is True
        assert retrieved.id == room.id

    def test_given_room_with_code_when_get_by_code_then_returns_room(self, db_session: Session):
        """
        given: room with specific code exists
        when: query by that code
        then: returns the correct room
        """
        # given
        room = Room(code="5678", is_active=True)
        db_session.add(room)
        db_session.commit()

        # when
        retrieved = db_session.query(Room).filter_by(code="5678").first()

        # then
        assert retrieved is not None
        assert retrieved.code == "5678"

    def test_given_no_room_with_code_when_get_by_code_then_returns_none(self, db_session: Session):
        """
        given: no room with code exists
        when: query by that code
        then: returns None
        """
        # when
        retrieved = db_session.query(Room).filter_by(code="9999").first()

        # then
        assert retrieved is None

    def test_given_room_saved_when_update_then_changes_persisted(self, db_session: Session):
        """
        given: room exists in database
        when: update room properties and commit
        then: changes are persisted
        """
        # given
        room = Room(code="9999", is_active=True)
        db_session.add(room)
        db_session.commit()

        # when
        room.is_active = False
        db_session.commit()

        # then
        retrieved = db_session.query(Room).filter_by(code="9999").first()
        assert retrieved.is_active is False
