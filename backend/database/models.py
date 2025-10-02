from datetime import UTC, datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LinkMetadata(Base):
    __tablename__ = "link_metadata"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    company_name: Mapped[str | None] = mapped_column(nullable=True)
    product_name: Mapped[str | None] = mapped_column(nullable=True)
    file_url: Mapped[str | None] = mapped_column(nullable=False)

    created_at: Mapped[str | None] = mapped_column(nullable=True, default=datetime.now(UTC).isoformat())
