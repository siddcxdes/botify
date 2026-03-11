from backend.database import engine, Base
from backend.models import User, SupportTicket, ChatHistory

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done! Tables created.")
