from app.logging.audit_logger import AuditLogger
from app.services.backend_client import BackendClient
from app.services.policy_store import PolicyStore
from app.services.quota_service import QuotaService

policy_store = PolicyStore()
quota_service = QuotaService()
audit_logger = AuditLogger()
backend_client = BackendClient()
