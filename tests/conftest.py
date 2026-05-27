"""
Pytest configuration for the auto-insurance project.

Sets up the Python path so that packages in packages/ can be imported
directly (e.g., `from rating_dsl import load_product`).
"""

import sys
from pathlib import Path

# Add packages/rating-dsl to sys.path so `from rating_dsl import ...` works
packages_dir = Path(__file__).parent.parent / "packages" / "rating-dsl"
sys.path.insert(0, str(packages_dir))
