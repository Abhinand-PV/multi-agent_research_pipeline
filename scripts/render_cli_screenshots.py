import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location(
    "capture_screenshots",
    ROOT / "scripts" / "capture_screenshots.py",
)
capture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture_module)
capture_cli_output_image = capture_module.capture_cli_output_image

root = ROOT

setup_output = (root / "docs" / "test_setup_output.txt").read_text(encoding="utf-8").strip()
capture_cli_output_image("python test_setup.py", setup_output, "cli-test-setup.png")

pipeline_output = (root / "docs" / "cli_pipeline_output.txt").read_text(encoding="utf-8")
summary = "\n".join(pipeline_output.splitlines()[:25])
summary += "\n\n... report content omitted for brevity ...\n\n"
summary += "\n".join(pipeline_output.splitlines()[-5:])
capture_cli_output_image('python main.py "renewable energy"', summary, "cli-pipeline.png")
