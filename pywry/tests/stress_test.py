
import time
import pytest
from pywry.app import PyWry
from pywry import runtime

def test_stress_lifecycle():
    """Rapidly create and destroy windows to checking for race conditions."""
    failures = 0
    iterations = 20
    
    print(f"\nStarting stress test with {iterations} iterations...")
    
    for i in range(iterations):
        try:
            print(f"Iteration {i+1}...", end="", flush=True)
            app = PyWry()
            
            # Show a window
            app.show("<div>Stress Test</div>")
            
            # Brief wait to let it render
            time.sleep(0.1)
            
            # Check if open
            if not app.is_open():
                print(" FAILED (not open)")
                failures += 1
            else:
                print(" OK", end="")
            
            # Destroy
            app.destroy()
            
            # Check cleanup
            if app.is_open():
                print(" FAILED (didn't close)")
                failures += 1
            else:
                print(" CLOSED")
                
        except Exception as e:
            print(f" ERROR: {e}")
            failures += 1
            
        # cleanup between runs similar to test fixture
        runtime.stop()
        time.sleep(0.1)

    print(f"\nStress test complete. Failures: {failures}/{iterations}")
    assert failures == 0
