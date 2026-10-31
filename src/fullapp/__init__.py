def main() -> None:
    import subprocess
    import sys
    from pathlib import Path

    app_path = Path(__file__).resolve().parents[2] / "app.py"
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        check=False,
    )
    raise SystemExit(result.returncode)
