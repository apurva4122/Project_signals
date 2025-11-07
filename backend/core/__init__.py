"""Core domain logic for Project Signals."""

from .execution.engine import SimulationEngine, SimulationResult
from .backtesting.runner import BacktestConfig, BacktestResult, BacktestRunner
from .portfolio.account import AccountState, PortfolioManager

__all__ = [
    "SimulationEngine",
    "SimulationResult",
    "BacktestConfig",
    "BacktestResult",
    "BacktestRunner",
    "PortfolioManager",
    "AccountState",
]


