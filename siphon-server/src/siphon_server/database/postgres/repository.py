from contextlib import contextmanager
from sqlalchemy.exc import IntegrityError
from siphon_api.models import ProcessedContent
from siphon_server.database.postgres.connection import SessionLocal
from siphon_server.database.postgres.models import ProcessedContentORM
from siphon_server.database.postgres.converters import to_orm, from_orm
import logging

logger = logging.getLogger(__name__)


class ContentRepository:
    """Self-managing repository with automatic session handling."""

    @contextmanager
    def _session(self):
        """Internal session context manager."""
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get(self, uri: str) -> ProcessedContent | None:
        """Get content by URI. Returns None if not found."""
        with self._session() as db:
            orm_obj = db.query(ProcessedContentORM).filter_by(uri=uri).first()
            return from_orm(orm_obj) if orm_obj else None

    def exists(self, uri: str) -> bool:
        """Check if content exists without loading data."""
        with self._session() as db:
            return db.query(
                db.query(ProcessedContentORM).filter_by(uri=uri).exists()
            ).scalar()

    def set(self, pc: ProcessedContent) -> None:
        """Create or update content."""
        with self._session() as db:
            existing = (
                db.query(ProcessedContentORM).filter_by(uri=pc.source.uri).first()
            )

            if existing:
                # Update
                for key, value in to_orm(pc).__dict__.items():
                    if key not in ("id", "_sa_instance_state"):
                        setattr(existing, key, value)
                db.commit()
                db.refresh(existing)
                logger.info(f"Updated content: {pc.source.uri}")
            else:
                # Create
                orm_obj = to_orm(pc)
                db.add(orm_obj)
                try:
                    db.commit()
                    db.refresh(orm_obj)
                    logger.info(f"Created content: {pc.source.uri}")
                except IntegrityError:
                    db.rollback()
                    raise ValueError(f"Content with URI {pc.source.uri} already exists")

    def create(self, pc: ProcessedContent) -> ProcessedContent:
        """Create new content. Raises ValueError if URI already exists."""
        with self._session() as db:
            orm_obj = to_orm(pc)
            db.add(orm_obj)
            try:
                db.commit()
                db.refresh(orm_obj)
                logger.info(f"Created content: {pc.source.uri}")
                return from_orm(orm_obj)
            except IntegrityError:
                db.rollback()
                raise ValueError(f"Content with URI {pc.source.uri} already exists")

    def update(self, pc: ProcessedContent) -> ProcessedContent:
        """Update existing content. Raises ValueError if not found."""
        with self._session() as db:
            existing = (
                db.query(ProcessedContentORM).filter_by(uri=pc.source.uri).first()
            )
            if not existing:
                raise ValueError(f"Content with URI {pc.source.uri} not found")

            for key, value in to_orm(pc).__dict__.items():
                if key not in ("id", "_sa_instance_state"):
                    setattr(existing, key, value)

            db.commit()
            db.refresh(existing)
            logger.info(f"Updated content: {pc.source.uri}")
            return from_orm(existing)

    def get_existing_uris(self, uris: list[str]) -> list[str]:
        """Batch check which URIs exist. Returns list of existing URIs."""
        with self._session() as db:
            results = (
                db.query(ProcessedContentORM.uri)
                .filter(ProcessedContentORM.uri.in_(uris))
                .all()
            )
            return [row.uri for row in results]

    # Archival methods for cli
    def get_last_processed_content(self) -> ProcessedContent | None:
        """Get the last processed content based on creation time."""
        with self._session() as db:
            orm_obj = (
                db.query(ProcessedContentORM)
                .order_by(ProcessedContentORM.created_at.desc())
                .first()
            )
            return from_orm(orm_obj) if orm_obj else None
