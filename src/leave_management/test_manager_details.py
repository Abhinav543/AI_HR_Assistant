
from src.leave_management.leave_database import get_pending_request_details

requests = get_pending_request_details()

print("\n========== MANAGER REQUEST DETAILS ==========")

for request in requests:
    print(request)
