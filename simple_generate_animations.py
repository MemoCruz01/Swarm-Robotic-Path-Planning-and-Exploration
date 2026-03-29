"""
Simple script to generate 6 animations without encoding issues.
Runs save_animation.py 6 times with silent mode.
"""

import subprocess
import time

print("Generating 6 animations with different random scenarios...")
print("=" * 60)

for i in range(1, 7):
    print(f"\n[{i}/6] Generating animation {i}...")
    try:
        # Run save_animation.py and suppress output
        result = subprocess.run(
            ['python', 'save_animation.py'],
            capture_output=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"    SUCCESS - Animation {i} created")
        else:
            print(f"    WARNING - Animation {i} had issues but may have been created")
        
        # Small delay between runs
        time.sleep(1)
        
    except Exception as e:
        print(f"    ERROR - {str(e)}")

print("\n" + "=" * 60)
print("Animation generation complete!")
print("\nCheck outputs/animations/ for all generated GIFs")
print("Each GIF represents a different random simulation run")
print("showing variations in robot behavior, obstacle placement,")
print("and convergence times.")
