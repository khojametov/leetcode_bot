from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker
from asyncio import current_task

async_session_factory = sessionmaker(class_=AsyncSession)
TestSession = async_scoped_session(async_session_factory, scopefunc=current_task)
