"""
Winner Validator Service — server-side validation of Bingo wins.

CRITICAL: This is server-authoritative. Never trust client winner claims.
"""

import json
from typing import List, Optional, Set, Tuple

from backend.models.bingo_models import WinPattern
from backend.core.logging import get_logger

logger = get_logger(__name__)


class WinnerValidatorService:
    """Server-authoritative winner validation for Bingo."""

    FREE_POSITION = (2, 2)  # Center cell is always marked

    def validate_winner(
        self,
        cartela_json: str,
        called_numbers: Set[int],
    ) -> Tuple[bool, Optional[WinPattern]]:
        """
        Validate if a cartela is a winner based on called numbers.
        
        Args:
            cartela_json: JSON string of 5x5 cartela
            called_numbers: Set of numbers that have been called
            
        Returns:
            (is_winner, win_pattern)
        """
        try:
            cartela = json.loads(cartela_json)
        except json.JSONDecodeError:
            logger.error("Invalid cartela JSON")
            return False, None

        # Check each win pattern in order of complexity
        if self._check_row_win(cartela, called_numbers):
            return True, WinPattern.ROW
        
        if self._check_column_win(cartela, called_numbers):
            return True, WinPattern.COLUMN
        
        if self._check_diagonal_win(cartela, called_numbers):
            return True, WinPattern.DIAGONAL
        
        if self._check_full_card_win(cartela, called_numbers):
            return True, WinPattern.FULL_CARD
        
        return False, None

    def _is_marked(self, number: int, called_numbers: Set[int]) -> bool:
        """Check if a number is marked (either called or FREE)."""
        return number == 0 or number in called_numbers

    def _check_row_win(self, cartela: List[List[int]], called_numbers: Set[int]) -> bool:
        """Check if any row is complete."""
        for row_idx, row in enumerate(cartela):
            if all(self._is_marked(num, called_numbers) for num in row):
                logger.info(f"Row win detected at row {row_idx}")
                return True
        return False

    def _check_column_win(self, cartela: List[List[int]], called_numbers: Set[int]) -> bool:
        """Check if any column is complete."""
        for col_idx in range(5):
            column = [cartela[row][col_idx] for row in range(5)]
            if all(self._is_marked(num, called_numbers) for num in column):
                logger.info(f"Column win detected at column {col_idx}")
                return True
        return False

    def _check_diagonal_win(self, cartela: List[List[int]], called_numbers: Set[int]) -> bool:
        """Check if either diagonal is complete."""
        # Top-left to bottom-right
        diagonal1 = [cartela[i][i] for i in range(5)]
        if all(self._is_marked(num, called_numbers) for num in diagonal1):
            logger.info("Diagonal win detected (top-left to bottom-right)")
            return True
        
        # Top-right to bottom-left
        diagonal2 = [cartela[i][4 - i] for i in range(5)]
        if all(self._is_marked(num, called_numbers) for num in diagonal2):
            logger.info("Diagonal win detected (top-right to bottom-left)")
            return True
        
        return False

    def _check_full_card_win(self, cartela: List[List[int]], called_numbers: Set[int]) -> bool:
        """Check if entire card is complete (blackout)."""
        for row in cartela:
            for num in row:
                if not self._is_marked(num, called_numbers):
                    return False
        
        logger.info("Full card win detected")
        return True

    def get_marked_numbers(
        self,
        cartela_json: str,
        called_numbers: Set[int],
    ) -> List[int]:
        """
        Calculate which numbers on a cartela are marked.
        
        Args:
            cartela_json: JSON string of 5x5 cartela
            called_numbers: Set of numbers that have been called
            
        Returns:
            List of marked numbers (including 0 for FREE)
        """
        try:
            cartela = json.loads(cartela_json)
        except json.JSONDecodeError:
            logger.error("Invalid cartela JSON")
            return []

        marked = []
        for row in cartela:
            for num in row:
                if self._is_marked(num, called_numbers):
                    marked.append(num)
        
        return marked
