from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from zipfile import ZipFile

import pytest

# The maintenance scripts are not part of the installed package, so they are
# imported from the repository checkout by path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from bump_version import add_changelog_entry, icon_count, set_version  # noqa: E402
from check_upstream_version import emit, is_newer  # noqa: E402
from icon_slugs import summarise  # noqa: E402


class TestIsNewer:
    @pytest.mark.parametrize(
        ("upstream", "bundled", "expected"),
        [
            ("16.27.0", "16.26.0", True),
            ("16.26.0", "16.26.0", False),
            # Never sync backwards to an older upstream.
            ("16.25.0", "16.26.0", False),
            # Our own fixes append a fourth segment, so upstream re-releasing
            # the version we patched must not trigger a downgrade.
            ("16.26.0", "16.26.0.1", False),
            ("16.26.1", "16.26.0.1", True),
            ("16.26.0.1", "16.26.0", True),
            ("17.0.0", "16.26.0", True),
            # Numeric, not lexicographic.
            ("2.0.0", "10.0.0", False),
            ("10.0.0", "2.0.0", True),
        ],
    )
    def test_comparison(self, upstream, bundled, expected):
        assert is_newer(upstream, bundled) is expected

    def test_differing_segment_counts(self):
        assert is_newer("16.27", "16.26.9") is True


class TestEmit:
    def test_writes_github_output(self, tmp_path, monkeypatch, capsys):
        output = tmp_path / "out.txt"
        monkeypatch.setenv("GITHUB_OUTPUT", str(output))

        emit(bundled="16.26.0", upstream="16.27.0", sync="true")

        assert output.read_text() == "bundled=16.26.0\nupstream=16.27.0\nsync=true\n"
        assert "sync=true" in capsys.readouterr().out

    def test_without_github_output(self, monkeypatch, capsys):
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)

        emit(sync="false")

        assert "sync=false" in capsys.readouterr().out

    @pytest.mark.parametrize("value", ["x\nsync=true", "x\rsync=true"])
    def test_refuses_newlines(self, value, tmp_path, monkeypatch):
        # A newline would let a crafted --upstream invent extra step outputs.
        output = tmp_path / "out.txt"
        monkeypatch.setenv("GITHUB_OUTPUT", str(output))

        with pytest.raises(SystemExit):
            emit(upstream=value)

        assert not output.exists()


class TestSummarise:
    def test_added_and_removed(self):
        result = summarise({"django", "gone"}, {"django", "new"})

        assert "2 icons before, 2 after." in result
        assert "### Removed (1)" in result
        assert "`gone`" in result
        assert "### Added (1)" in result
        assert "breaking change" in result

    def test_no_change(self):
        result = summarise({"django"}, {"django"})

        assert "No slugs added or removed" in result
        assert "Removed" not in result

    def test_additions_alone_carry_no_warning(self):
        result = summarise({"django"}, {"django", "new"})

        assert "breaking change" not in result

    def test_long_lists_are_truncated(self):
        after = {f"brand{index}" for index in range(60)}

        result = summarise(set(), after)

        assert "### Added (60)" in result
        assert "...and 10 more." in result


class TestBumpVersion:
    def test_set_version(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "x"\nversion = "16.26.0"\n')

        set_version(pyproject, "16.27.0")

        assert 'version = "16.27.0"' in pyproject.read_text()

    def test_set_version_without_a_match(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "x"\n')

        with pytest.raises(SystemExit):
            set_version(pyproject, "16.27.0")

    def test_add_changelog_entry(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## 16.26.0 (2026-07-19)\n\nOld.\n")

        add_changelog_entry(changelog, "16.27.0", 3450, date(2026, 7, 20))

        text = changelog.read_text()
        assert text.startswith("# Changelog\n\n## 16.27.0 (2026-07-20)\n")
        assert "- Bundled Simple Icons 16.27.0 (3,450 icons).\n" in text
        # The previous entry survives, below the new one.
        assert text.index("16.27.0") < text.index("16.26.0")

    def test_add_changelog_entry_refuses_duplicates(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n\n## 16.27.0 (2026-07-20)\n\nAlready.\n")

        with pytest.raises(SystemExit):
            add_changelog_entry(changelog, "16.27.0", 3450, date(2026, 7, 20))

    def test_add_changelog_entry_requires_the_heading(self, tmp_path):
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("Notes\n")

        with pytest.raises(SystemExit):
            add_changelog_entry(changelog, "16.27.0", 3450, date(2026, 7, 20))

    def test_icon_count(self, tmp_path):
        archive_path = tmp_path / "icons.zip"
        with ZipFile(archive_path, "w") as archive:
            archive.writestr("data.json", "{}")
            archive.writestr("icons/django.svg", "<svg/>")
            archive.writestr("icons/react.svg", "<svg/>")

        assert icon_count(archive_path) == 2
