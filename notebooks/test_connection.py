#!/usr/bin/env python3
"""Test script to verify notebook database connection setup."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test imports
try:
    from backend.config import settings
    from backend.models import PnLHistory, AccountSnapshot, Position, Trade, PerformanceMetric
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.orm import sessionmaker
    
    print('✓ All imports successful')
    print(f'✓ Database URL: {settings.database.url}')
    
    # Test database connection
    if settings.database.url.startswith('sqlite'):
        engine = create_engine(
            settings.database.url,
            connect_args={'check_same_thread': False},
            echo=False,
        )
    else:
        engine = create_engine(settings.database.url, echo=False)
    
    # Test connection
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f'✓ Database connection successful')
        print(f'✓ Available tables: {", ".join(tables)}')
        
        # Check if pnl_history table exists and has data
        if 'pnl_history' in tables:
            from sqlalchemy import text
            result = conn.execute(text('SELECT COUNT(*) FROM pnl_history'))
            count = result.fetchone()[0]
            print(f'✓ pnl_history table exists with {count} records')
        
        # Test session creation
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with SessionLocal() as session:
            pnl_count = session.query(PnLHistory).count()
            print(f'✓ SQLAlchemy ORM query successful: {pnl_count} PnL records')
    
    print('\n✓ All tests passed! Notebook should be able to connect to the database.')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
