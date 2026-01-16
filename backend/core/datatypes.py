from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

# ENUMS
class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

# ORDER
@dataclass(order=True)
class Order:
    # sort_index for the Heap to sort orders automatically.
    # hiding it from the __init__ because it's calculated automatically.
    sort_index: float = field(init=False, repr=False)
    
    price: float
    quantity: float
    side: Side
    order_type: OrderType
    
    # Generate unique ID and timestamp automatically
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    timestamp: float = field(default_factory=time.time, compare=False)

    def __post_init__(self):
        """
        The 'Magic' for O(1) Priority:
        - Bids (Buys): We want Highest Price first so we multiply by -1 so Min-Heap sorts it to top.
        - Asks (Sells): We want Lowest Price first. Keep as is.
        """
        if self.side == Side.BUY:
            self.sort_index = -self.price
        else:
            self.sort_index = self.price

# TRADE
@dataclass
class Trade:
    price: float
    quantity: float
    buyer_order_id: str
    seller_order_id: str
    timestamp: float = field(default_factory=time.time)
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))