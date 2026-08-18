"""
Cartela Generator Service — generates valid 5x5 Bingo cartelas.

Standard 75-ball Bingo rules:
- B: 1-15
- I: 16-30
- N: 31-45 (center is FREE)
- G: 46-60
- O: 61-75
"""

import json
import secrets
from typing import List

from backend.core.logging import get_logger

logger = get_logger(__name__)


class CartelaGeneratorService:
    """Generate valid 5x5 Bingo cartelas with correct B-I-N-G-O ranges."""

    # Column ranges for 75-ball Bingo
    COLUMN_RANGES = {
        0: (1, 15),    # B
        1: (16, 30),   # I
        2: (31, 45),   # N
        3: (46, 60),   # G
        4: (61, 75),   # O
    }

    COLUMN_LETTERS = ['B', 'I', 'N', 'G', 'O']
    FREE_POSITION = (2, 2)  # Center cell (row 2, col 2)

    def generate_cartela(self) -> List[List[int]]:
        """
        Generate a random 5x5 Bingo cartela.
        
        Returns:
            5x5 grid where center cell is 0 (FREE).
        """
        cartela = []
        
        for col_idx in range(5):
            min_val, max_val = self.COLUMN_RANGES[col_idx]
            
            # Generate 5 unique numbers for this column
            column_numbers = self._generate_unique_numbers(min_val, max_val, 5)
            
            # If this is column N (index 2), replace center with 0 (FREE)
            if col_idx == 2:
                column_numbers[2] = 0
            
            cartela.append(column_numbers)
        
        # Transpose to get row-major format
        transposed = [[cartela[col][row] for col in range(5)] for row in range(5)]
        
        return transposed

    def _generate_unique_numbers(self, min_val: int, max_val: int, count: int) -> List[int]:
        """
        Generate a list of unique random numbers within a range.
        
        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
            count: Number of unique values to generate
            
        Returns:
            Sorted list of unique numbers
        """
        # Use secrets for cryptographically secure random generation
        available = list(range(min_val, max_val + 1))
        selected = []
        
        for _ in range(count):
            idx = secrets.randbelow(len(available))
            selected.append(available.pop(idx))
        
        return sorted(selected)

    def generate_cartela_json(self) -> str:
        """
        Generate a cartela and return it as JSON string.
        
        Returns:
            JSON array string representing the 5x5 cartela
        """
        cartela = self.generate_cartela()
        return json.dumps(cartela)

    def generate_cartela_number(self, game_id: int, user_id: int) -> str:
        """
        Generate a unique cartela identifier.
        
        Args:
            game_id: Game ID
            user_id: User ID
            
        Returns:
            Cartela number in format: "G{game_id}-U{user_id}-{random}"
        """
        random_suffix = secrets.token_hex(4).upper()
        return f"G{game_id}-U{user_id}-{random_suffix}"

    def validate_cartela(self, cartela: List[List[int]]) -> bool:
        """
        Validate a cartela structure.
        
        Args:
            cartela: 5x5 grid to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check dimensions
        if len(cartela) != 5:
            logger.error("Invalid cartela: must have 5 rows")
            return False
        
        for row_idx, row in enumerate(cartela):
            if len(row) != 5:
                logger.error(f"Invalid cartela: row {row_idx} must have 5 columns")
                return False
        
        # Check center is FREE (0)
        if cartela[2][2] != 0:
            logger.error("Invalid cartela: center cell must be FREE (0)")
            return False
        
        # Check column ranges and uniqueness
        all_numbers = set()
        
        for col_idx in range(5):
            min_val, max_val = self.COLUMN_RANGES[col_idx]
            column_numbers = [cartela[row][col_idx] for row in range(5)]
            
            for row_idx, num in enumerate(column_numbers):
                # Skip FREE cell
                if row_idx == 2 and col_idx == 2:
                    continue
                
                # Check range
                if not (min_val <= num <= max_val):
                    logger.error(
                        f"Invalid cartela: number {num} at ({row_idx},{col_idx}) "
                        f"outside range {min_val}-{max_val}"
                    )
                    return False
                
                # Check uniqueness
                if num in all_numbers:
                    logger.error(f"Invalid cartela: duplicate number {num}")
                    return False
                
                all_numbers.add(num)
        
        return True

    def get_column_letter(self, number: int) -> str:
        """
        Get the column letter (B/I/N/G/O) for a given number.
        
        Args:
            number: Number between 1-75
            
        Returns:
            Column letter
        """
        if 1 <= number <= 15:
            return 'B'
        elif 16 <= number <= 30:
            return 'I'
        elif 31 <= number <= 45:
            return 'N'
        elif 46 <= number <= 60:
            return 'G'
        elif 61 <= number <= 75:
            return 'O'
        else:
            raise ValueError(f"Number {number} is outside valid range 1-75")
