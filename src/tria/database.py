"""SQLite local, migraciones aditivas y trazabilidad histórica por ejecución."""
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from sqlalchemy import (Table, Column, String, Integer, MetaData, ForeignKey,
                        Text, create_engine, select, func, text)

SCHEMA = MetaData()
studies = Table('studies', SCHEMA,
    Column('id', String, primary_key=True), Column('sha256', String(64), nullable=False),
    Column('source_format', String(10), nullable=False), Column('width', Integer, nullable=False),
    Column('height', Integer, nullable=False), Column('created_at', String(40), nullable=False),
    Column('warnings', Text, nullable=False), Column('provenance', Text, nullable=True))
analyses = Table('analyses', SCHEMA,
    Column('id', String, primary_key=True),
    Column('study_id', String, ForeignKey('studies.id'), nullable=False),
    Column('created_at', String(40), nullable=False), Column('mode', String, nullable=False),
    Column('model_version', String, nullable=False), Column('status', String, nullable=False),
    Column('scores', Text, nullable=False), Column('features', Text, nullable=False),
    Column('indicator', String, nullable=False), Column('message', Text, nullable=False),
    Column('weights_sha256', String(64), nullable=True),
    Column('software_revision', String(64), nullable=True),
    Column('gradcam_target', String(32), nullable=True))
events = Table('audit_events', SCHEMA,
    Column('id', String, primary_key=True),
    Column('study_id', String, ForeignKey('studies.id'), nullable=False),
    Column('event', String, nullable=False), Column('created_at', String(40), nullable=False))

# Explicit whitelist for backward-compatible, additive migrations; never drop data.
_NEW_COLUMNS = {
    'studies': {'provenance': 'TEXT'},
    'analyses': {
        'weights_sha256': 'VARCHAR(64)',
        'software_revision': 'VARCHAR(64)',
        'gradcam_target': 'VARCHAR(32)',
    },
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def open_database(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine('sqlite+pysqlite:///' + str(path.absolute()), connect_args={'check_same_thread': False})
    # For existing installations SCHEMA.create_all does not add columns.
    # Add only known nullable columns so old studies and analyses remain readable.
    with engine.begin() as c:
        for table, columns in _NEW_COLUMNS.items():
            existing = {r[1] for r in c.exec_driver_sql(f'PRAGMA table_info("{table}")')}
            for column, sql_type in columns.items():
                if existing and column not in existing:
                    c.exec_driver_sql(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {sql_type}')
    SCHEMA.create_all(engine)
    return engine


def insert_study(engine, record):
    with engine.begin() as c:
        c.execute(studies.insert().values(**record))
        c.execute(events.insert().values(id=str(uuid.uuid4()), study_id=record['id'],
                                          event='STUDY_IMPORTED', created_at=utc_now()))


def insert_analysis(engine, record):
    with engine.begin() as c:
        c.execute(analyses.insert().values(**record))
        c.execute(events.insert().values(id=str(uuid.uuid4()), study_id=record['study_id'],
                                          event='ANALYSIS_' + record['status'], created_at=utc_now()))


def _study(row):
    return {**row, 'warnings': json.loads(row['warnings']),
            'provenance': json.loads(row['provenance']) if row['provenance'] else
            {'status': 'sin_acreditar', 'label': 'Procedencia no registrada en versión anterior'}} if row else None


def _analysis(row):
    return {**row, 'scores': json.loads(row['scores']), 'features': json.loads(row['features'])} if row else None


def get_study(engine, study_id):
    with engine.connect() as c:
        row = c.execute(select(studies).where(studies.c.id == study_id)).mappings().first()
    return _study(row)


def list_studies(engine):
    with engine.connect() as c:
        rows = c.execute(select(studies).order_by(studies.c.created_at.desc()).limit(50)).mappings().all()
    return [_study(row) for row in rows]


def get_analysis(engine, analysis_id):
    with engine.connect() as c:
        row = c.execute(select(analyses).where(analyses.c.id == analysis_id)).mappings().first()
    return _analysis(row)


def list_analyses(engine, study_id):
    with engine.connect() as c:
        rows = c.execute(select(analyses).where(analyses.c.study_id == study_id)
                         .order_by(analyses.c.created_at.desc(), analyses.c.id.desc())).mappings().all()
    return [_analysis(row) for row in rows]


def counts(engine):
    with engine.connect() as c:
        s = c.scalar(select(func.count()).select_from(studies))
        a = c.scalar(select(func.count()).select_from(analyses))
    return {'studies': s, 'analyses': a}
