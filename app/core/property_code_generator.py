from sqlalchemy.orm import Session
from app.domain.property_models import Property
import logging

logger = logging.getLogger(__name__)

class PropertyCodeGenerator:
    
    @staticmethod
    def generate_property_code(db: Session) -> str:
        """
        Generate a unique property code in the format COL0000001.
        
        Returns:
            str: A unique property code
        """
        try:
            # Get the highest existing property code
            latest_property = db.query(Property).order_by(Property.property_code.desc()).first()
            
            if latest_property:
                # Extract the numeric part from the latest code
                try:
                    numeric_part = int(latest_property.property_code[3:])  # Skip 'COL'
                    next_number = numeric_part + 1
                except (ValueError, IndexError):
                    # If parsing fails, start from 1
                    next_number = 1
            else:
                # No existing properties, start from 1
                next_number = 1
            
            # Format the new code
            property_code = f"COL{next_number:07d}"
            
            # Ensure uniqueness (in case of concurrent requests)
            while db.query(Property).filter(Property.property_code == property_code).first():
                next_number += 1
                property_code = f"COL{next_number:07d}"
            
            return property_code
            
        except Exception as e:
            logger.error(f"Error generating property code: {e}")
            raise Exception("Failed to generate property code")
    
    @staticmethod
    def validate_property_code(property_code: str) -> bool:
        """
        Validate if a property code follows the correct format.
        
        Args:
            property_code (str): The property code to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not property_code:
            return False
        
        # Check if it starts with 'COL' and has 7 digits
        if len(property_code) != 10:
            return False
        
        if not property_code.startswith('COL'):
            return False
        
        try:
            numeric_part = int(property_code[3:])
            return 1 <= numeric_part <= 9999999
        except ValueError:
            return False 