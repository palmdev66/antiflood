from yoomoney import Authorize
from config import YOOMONEY_CLIENT_ID, YOOMONEY_REDIRECT_URI

Authorize(
      client_id=YOOMONEY_CLIENT_ID,
      redirect_uri=YOOMONEY_REDIRECT_URI,
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )