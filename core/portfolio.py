"""Portfolio class for managing trading positions."""
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from utils.logger import Logger


class Position:
    """Represents a single trading position."""
    
    def __init__(self, ticker: str, quantity: float, entry_price: float, entry_time: datetime):
        """
        Initialize position.
        
        Args:
            ticker: Ticker symbol
            quantity: Position quantity (positive for long, negative for short)
            entry_price: Entry price
            entry_time: Entry timestamp
        """
        self.ticker = ticker
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.is_open = True
    
    def close(self, exit_price: float, exit_time: datetime):
        """
        Close the position.
        
        Args:
            exit_price: Exit price
            exit_time: Exit timestamp
        """
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.is_open = False
    
    def get_pnl(self, current_price: Optional[float] = None) -> float:
        """
        Calculate profit/loss.
        
        Args:
            current_price: Current price (for open positions)
        
        Returns:
            Profit/loss amount
        """
        price = current_price if self.is_open else self.exit_price
        if price is None:
            return 0.0
        return (price - self.entry_price) * self.quantity
    
    def get_return_pct(self, current_price: Optional[float] = None) -> float:
        """
        Calculate return percentage.
        
        Args:
            current_price: Current price (for open positions)
        
        Returns:
            Return percentage
        """
        price = current_price if self.is_open else self.exit_price
        if price is None:
            return 0.0
        return ((price - self.entry_price) / self.entry_price) * 100


class Portfolio:
    """Portfolio manager for tracking positions and performance."""
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Initial capital amount
        """
        self.initial_capital = initial_capital
        self._cash = initial_capital
        self._positions: Dict[str, List[Position]] = {}
        self._closed_positions: List[Position] = []
        self._logger = Logger()
    
    @property
    def cash(self) -> float:
        """Get current cash."""
        return self._cash
    
    @property
    def positions(self) -> Dict[str, List[Position]]:
        """Get open positions."""
        return self._positions
    
    @property
    def closed_positions(self) -> List[Position]:
        """Get closed positions."""
        return self._closed_positions
    
    def open_position(self, ticker: str, quantity: float, price: float, time: datetime) -> bool:
        """
        Open a new position.
        
        Args:
            ticker: Ticker symbol
            quantity: Position quantity
            price: Entry price
            time: Entry timestamp
        
        Returns:
            True if successful, False otherwise
        """
        cost = abs(quantity) * price
        
        if cost > self._cash:
            self._logger.warning(f"Insufficient cash to open position: {ticker}")
            return False
        
        position = Position(ticker, quantity, price, time)
        
        if ticker not in self._positions:
            self._positions[ticker] = []
        
        self._positions[ticker].append(position)
        self._cash -= cost
        self._logger.info(f"Opened position: {ticker} x{quantity} @ {price}")
        
        return True
    
    def close_position(self, ticker: str, quantity: float, price: float, time: datetime) -> bool:
        """
        Close a position (or part of it).
        
        Args:
            ticker: Ticker symbol
            quantity: Quantity to close (positive for long, negative for short)
            price: Exit price
            time: Exit timestamp
        
        Returns:
            True if successful, False otherwise
        """
        if ticker not in self._positions or not self._positions[ticker]:
            self._logger.warning(f"No open positions for {ticker}")
            return False
        
        # Find matching position
        for position in self._positions[ticker]:
            if position.is_open and position.quantity * quantity > 0:  # Same direction
                close_qty = min(abs(quantity), abs(position.quantity))
                
                if abs(close_qty) < abs(position.quantity):
                    # Partial close - create new position with remaining quantity
                    remaining_qty = position.quantity - (close_qty if quantity > 0 else -close_qty)
                    new_position = Position(ticker, remaining_qty, position.entry_price, position.entry_time)
                    self._positions[ticker].append(new_position)
                
                position.close(price, time)
                self._cash += abs(close_qty) * price
                self._closed_positions.append(position)
                self._logger.info(f"Closed position: {ticker} x{close_qty} @ {price}")
                return True
        
        return False
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            current_prices: Dictionary of ticker -> current price
        
        Returns:
            Total portfolio value
        """
        total = self._cash
        
        for ticker, positions in self._positions.items():
            if ticker in current_prices:
                for position in positions:
                    if position.is_open:
                        total += position.quantity * current_prices[ticker]
        
        return total
    
    def get_total_pnl(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total profit/loss.
        
        Args:
            current_prices: Dictionary of ticker -> current price
        
        Returns:
            Total PnL
        """
        pnl = 0.0
        
        # Closed positions
        for position in self._closed_positions:
            pnl += position.get_pnl()
        
        # Open positions
        for ticker, positions in self._positions.items():
            if ticker in current_prices:
                for position in positions:
                    if position.is_open:
                        pnl += position.get_pnl(current_prices[ticker])
        
        return pnl
    
    def get_return_pct(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total return percentage.
        
        Args:
            current_prices: Dictionary of ticker -> current price
        
        Returns:
            Return percentage
        """
        total_value = self.get_total_value(current_prices)
        return ((total_value - self.initial_capital) / self.initial_capital) * 100

