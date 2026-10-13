"""Report Python and NVIDIA visibility without installing ML dependencies."""

import platform
import shutil
import subprocess
import sys


def main():
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    compatible = sys.version_info[:2] == (3, 11)
    print(f"Python 3.11 compatible: {compatible}")
    executable = shutil.which("nvidia-smi")
    if executable is None:
        print("GPU: nvidia-smi unavailable; GPU/CUDA not verified.")
    else:
        try:
            result = subprocess.run(
                [executable, "--query-gpu=name,driver_version,memory.total", "--format=csv"],
                capture_output=True, text=True, timeout=15, check=True,
            )
            print(f"GPU (driver visibility only):\n{result.stdout.strip()}")
        except (OSError, subprocess.SubprocessError) as error:
            print(f"GPU: inspection failed ({error}); GPU/CUDA not verified.")
    print("PyTorch/CUDA training compatibility: not checked.")
    return 0 if compatible else 1


if __name__ == "__main__":
    raise SystemExit(main())
