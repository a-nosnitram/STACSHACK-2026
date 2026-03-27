import sys
import subprocess


if __name__ == "__main__":
    cmd = [sys.executable, "-m", "pwp_game"] + sys.argv[1:]
    raise SystemExit(subprocess.call(cmd))
