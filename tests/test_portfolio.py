"""Tests for Portfolio class."""
import pytest
from datetime import datetime
from core.portfolio import Portfolio, Position


class TestPosition:
    """Test cases for Position class."""
    
    def test_init(self):
        """Test Position initialization."""
        pos = Position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        assert pos.ticker == 'AAPL'
        assert pos.quantity == 10
        assert pos.entry_price == 100.0
        assert pos.is_open is True
    
    def test_close(self):
        """Test closing position."""
        pos = Position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        pos.close(110.0, datetime(2024, 1, 2))
        assert pos.is_open is False
        assert pos.exit_price == 110.0
    
    def test_get_pnl_open(self):
        """Test PnL calculation for open position."""
        pos = Position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        pnl = pos.get_pnl(110.0)
        assert pnl == 100.0  # (110 - 100) * 10
    
    def test_get_pnl_closed(self):
        """Test PnL calculation for closed position."""
        pos = Position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        pos.close(110.0, datetime(2024, 1, 2))
        pnl = pos.get_pnl()
        assert pnl == 100.0
    
    def test_get_return_pct(self):
        """Test return percentage calculation."""
        pos = Position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        return_pct = pos.get_return_pct(110.0)
        assert return_pct == 10.0  # (110 - 100) / 100 * 100


class TestPortfolio:
    """Test cases for Portfolio class."""
    
    @pytest.fixture
    def portfolio(self):
        """Create Portfolio instance."""
        return Portfolio(initial_capital=100000.0)
    
    def test_init(self, portfolio):
        """Test Portfolio initialization."""
        assert portfolio.initial_capital == 100000.0
        assert portfolio.cash == 100000.0
        assert len(portfolio.positions) == 0
    
    def test_open_position(self, portfolio):
        """Test opening a position."""
        success = portfolio.open_position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        assert success is True
        assert portfolio.cash == 99000.0  # 100000 - (10 * 100)
        assert 'AAPL' in portfolio.positions
    
    def test_open_position_insufficient_cash(self, portfolio):
        """Test opening position with insufficient cash."""
        success = portfolio.open_position('AAPL', 10000, 100.0, datetime(2024, 1, 1))
        assert success is False
    
    def test_close_position(self, portfolio):
        """Test closing a position."""
        portfolio.open_position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        success = portfolio.close_position('AAPL', 10, 110.0, datetime(2024, 1, 2))
        assert success is True
        assert portfolio.cash == 100100.0  # 99000 + (10 * 110)
        assert len(portfolio.closed_positions) == 1
    
    def test_close_position_nonexistent(self, portfolio):
        """Test closing nonexistent position."""
        success = portfolio.close_position('AAPL', 10, 110.0, datetime(2024, 1, 2))
        assert success is False
    
    def test_get_total_value(self, portfolio):
        """Test getting total portfolio value."""
        portfolio.open_position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        current_prices = {'AAPL': 110.0}
        total_value = portfolio.get_total_value(current_prices)
        assert total_value == 100100.0  # 99000 cash + (10 * 110)
    
    def test_get_total_pnl(self, portfolio):
        """Test getting total PnL."""
        portfolio.open_position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        current_prices = {'AAPL': 110.0}
        pnl = portfolio.get_total_pnl(current_prices)
        assert pnl == 100.0  # (110 - 100) * 10
    
    def test_get_return_pct(self, portfolio):
        """Test getting return percentage."""
        portfolio.open_position('AAPL', 10, 100.0, datetime(2024, 1, 1))
        current_prices = {'AAPL': 110.0}
        return_pct = portfolio.get_return_pct(current_prices)
        assert return_pct == 0.1  # (100100 - 100000) / 100000 * 100

