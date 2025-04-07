from database.models import Email

def get_thread_context(thread_id, session):
    """
    Fetch all emails in the same thread ordered by date.
    
    Args:
        thread_id (str): The Gmail thread ID to fetch context for.
        session (Session): The SQLAlchemy DB session.
    
    Returns:
        List[Email]: List of Email objects in the thread.
    """
    return (
        session.query(Email)
        .filter_by(thread_id=thread_id)
        .order_by(Email.date.asc())
        .all()
    )
