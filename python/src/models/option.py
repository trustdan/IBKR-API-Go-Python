from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, Optional, List, Dict, Union


@dataclass
class Option:
    """Represents a single option contract."""
    symbol: str
    underlying: str
    option_type: Literal["call", "put"]
    strike: float
    expiration: date
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    
    @property
    def mid_price(self) -> float:
        """Calculate the mid-point price between bid and ask."""
        return (self.bid + self.ask) / 2
    
    @property
    def spread(self) -> float:
        """Calculate the bid-ask spread."""
        return self.ask - self.bid
    
    @property
    def spread_percentage(self) -> float:
        """Calculate the bid-ask spread as a percentage of the mid price."""
        if self.mid_price == 0:
            return float('inf')
        return (self.ask - self.bid) / self.mid_price * 100
    
    @property
    def days_to_expiration(self) -> int:
        """Calculate days to expiration from today."""
        today = datetime.now().date()
        return (self.expiration - today).days
    
    def __str__(self) -> str:
        return (f"{self.underlying} {self.expiration.strftime('%Y-%m-%d')} "
                f"{self.option_type.upper()} {self.strike:.2f}")


@dataclass
class OptionSpread:
    """Represents an option spread strategy."""
    symbol: str
    expiration: date
    spread_type: Literal["BULL_CALL", "BEAR_PUT"]
    long_leg: Option
    short_leg: Option
    cost: float  # Net debit/credit
    max_profit: float
    max_loss: float
    delta: float  # Net delta of the spread
    reward_risk_ratio: float = 0.0
    
    def __post_init__(self):
        if self.reward_risk_ratio == 0 and self.max_loss > 0:
            self.reward_risk_ratio = self.max_profit / self.max_loss
            
    @property
    def width(self) -> float:
        """Get the width of the spread (difference between strikes)."""
        return abs(self.long_leg.strike - self.short_leg.strike)
    
    @property
    def days_to_expiration(self) -> int:
        """Calculate days to expiration from today."""
        return self.long_leg.days_to_expiration
    
    def __str__(self) -> str:
        return (f"{self.spread_type} {self.symbol} {self.expiration.strftime('%Y-%m-%d')} "
                f"[{self.long_leg.strike:.2f}-{self.short_leg.strike:.2f}] "
                f"Cost: ${self.cost:.2f} R/R: {self.reward_risk_ratio:.2f}") 