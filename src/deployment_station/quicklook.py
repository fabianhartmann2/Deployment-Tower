"""Create a macOS Finder/Quick Look USDZ from the assembled CAD model."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .assembly import build_assembly
from .parameters import DEFAULT, StationParameters


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "exports" / "interactive" / "complete_assembly_finder.usdz"


def _required_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"required macOS USD tool is unavailable: {name}")
    return path


def _set_millimetre_scale(source: Path, destination: Path) -> None:
    text = source.read_text(encoding="utf-8")
    text, replacements = re.subn(
        r"(?m)^(\s*)metersPerUnit\s*=\s*1\s*$",
        r"\1metersPerUnit = 0.001",
        text,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError("GLB conversion did not expose the expected metersPerUnit metadata")
    destination.write_text(text, encoding="utf-8", newline="\n")


def export_quicklook_usdz(
    output: Path = DEFAULT_OUTPUT,
    p: StationParameters = DEFAULT,
    tolerance: float = 0.55,
    angular_tolerance: float = 0.20,
) -> Path:
    """Export all 15 installed parts and 10 equipment/interface references."""

    usdcat = _required_tool("usdcat")
    usdzip = _required_tool("usdzip")
    usdchecker = _required_tool("usdchecker")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="deployment_tower_quicklook_") as temp_name:
        temp = Path(temp_name)
        glb = temp / "complete_assembly.glb"
        converted_usda = temp / "converted.usda"
        scaled_usda = temp / "complete_assembly_finder.usda"
        root_usdc = temp / "complete_assembly_finder.usdc"
        packaged = temp / output.name

        assembly = build_assembly(p, include_references=True, include_handle=True)
        assembly.export(
            str(glb),
            exportType="GLTF",
            tolerance=tolerance,
            angularTolerance=angular_tolerance,
        )
        subprocess.run([usdcat, str(glb), "-o", str(converted_usda)], check=True)
        _set_millimetre_scale(converted_usda, scaled_usda)
        subprocess.run([usdcat, str(scaled_usda), "-o", str(root_usdc)], check=True)
        subprocess.run(
            [usdzip, "--arkitAsset", str(root_usdc), str(packaged)],
            check=True,
        )
        subprocess.run(
            [usdchecker, "--arkit", "--strict", str(packaged)],
            check=True,
        )
        packaged.replace(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tolerance", type=float, default=0.55)
    parser.add_argument("--angular-tolerance", type=float, default=0.20)
    args = parser.parse_args()
    output = export_quicklook_usdz(
        args.output,
        DEFAULT,
        args.tolerance,
        args.angular_tolerance,
    )
    print(f"exported {output} ({output.stat().st_size / (1024 * 1024):.1f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
