from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from siphon_api.models import ProcessedContent
from siphon_server.database.postgres.models import ProcessedContentORM
from siphon_server.database.postgres.converters import to_orm, from_orm
import logging

logger = logging.getLogger(__name__)


class ContentRepository:
    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy Session instance
        """
        logging.debug("ContentRepository initialized with DB session")
        self.db = db

    # Pipeline "cache-y" methods.
    def get(self, uri: str) -> ProcessedContent | None:
        return self.get_by_uri(uri)

    def set(self, pc: ProcessedContent) -> None:
        if self.exists(pc.source.uri):
            self.update(pc)
        else:
            self.create(pc)

    # Full CRUD methods.
    def get_by_uri(self, uri: str) -> ProcessedContent | None:
        """
        Fetch content by URI. Returns None if not found.
        """
        logging.debug(f"Fetching content for URI: {uri}")
        orm_obj = self.db.query(ProcessedContentORM).filter_by(uri=uri).first()
        return from_orm(orm_obj) if orm_obj else None

    def exists(self, uri: str) -> bool:
        """
        Check if content exists without loading data.
        """
        logging.debug(f"Checking existence for URI: {uri}")
        return self.db.query(
            self.db.query(ProcessedContentORM).filter_by(uri=uri).exists()
        ).scalar()

    def create(self, pc: ProcessedContent) -> ProcessedContent:
        """
        Create new content. Raises ValueError if URI already exists.
        """
        logging.debug(f"Creating content for URI: {pc.source.uri}")
        orm_obj = to_orm(pc)
        self.db.add(orm_obj)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Content with URI {pc.source.uri} already exists")
        self.db.refresh(orm_obj)
        return from_orm(orm_obj)

    def update(self, pc: ProcessedContent) -> ProcessedContent:
        """
        Update existing content. Raises ValueError if not found.
        """
        logging.debug(f"Updating content for URI: {pc.source.uri}")
        existing = (
            self.db.query(ProcessedContentORM).filter_by(uri=pc.source.uri).first()
        )
        if not existing:
            raise ValueError(f"Content with URI {pc.source.uri} not found")

        for key, value in to_orm(pc).__dict__.items():
            if key not in ("id", "_sa_instance_state"):
                setattr(existing, key, value)

        self.db.commit()
        self.db.refresh(existing)
        return from_orm(existing)

    def upsert(self, pc: ProcessedContent) -> ProcessedContent:
        """
        Update if exists, create if not.
        """
        logging.debug(f"Upserting content for URI: {pc.source.uri}")
        try:
            return self.update(pc)
        except ValueError:
            return self.create(pc)

    def get_existing_uris(self, uris: list[str]) -> list[str]:
        """
        Batch check which URIs exist. Returns list of existing URIs.
        """
        logging.debug(f"Checking existing URIs from list of {len(uris)} URIs")
        results = (
            self.db.query(ProcessedContentORM.uri)
            .filter(ProcessedContentORM.uri.in_(uris))
            .all()
        )
        return [row.uri for row in results]
