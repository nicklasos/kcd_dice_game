import sys
import os
from pathlib import Path

# Додаємо кореневу директорію проекту до sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Додаємо src директорію до sys.path
src_dir = root_dir / 'src'
sys.path.insert(0, str(src_dir))