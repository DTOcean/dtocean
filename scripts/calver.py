import re
import unittest.mock as mock
from datetime import datetime, timezone
from logging import Logger, getLogger
from typing import Any

from semantic_release import LevelBump
from semantic_release.__main__ import main
from semantic_release.version.version import Version

logger: Logger = getLogger("semantic_release")


CALVER_REGEX = re.compile(
    r"""
    (?P<major>[1-9][0-9]{3})
    \.
    (?P<minor>[1-9]|1[012])
    \.
    (?P<patch>0|[1-9]\d*)
    (?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
    (?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?
    """,
    flags=re.VERBOSE,
)


class CalVersion(Version):
    _VERSION_REGEX = CALVER_REGEX

    def __init__(self, *args, **kwargs):
        logger.info("Applying patched Version type")
        super().__init__(*args, **kwargs)

    def bump(self, level: Any) -> Version:
        """
        Return a new Version instance according to the level specified to bump.
        Note this will intentionally drop the build metadata - that should be added
        elsewhere for the specific build producing this version.
        """
        if not isinstance(level, LevelBump):
            raise TypeError(
                f"Unexpected level {level!r}: expected {LevelBump!r}"
            )

        if level == LevelBump.NO_RELEASE:
            return Version(
                self.major,
                self.minor,
                self.patch,
                prerelease_token=self.prerelease_token,
                prerelease_revision=self.prerelease_revision,
                tag_format=self.tag_format,
            )

        dt = datetime.now(timezone.utc)
        new_date = False
        if dt.year > self.major:
            new_date |= True
        if dt.month > self.minor:
            new_date |= True

        if level is LevelBump.PRERELEASE_REVISION:
            return Version(
                dt.year,
                dt.month,
                0 if new_date else self.patch,
                prerelease_token=self.prerelease_token,
                prerelease_revision=1
                if new_date or not self.is_prerelease
                else (self.prerelease_revision or 0) + 1,
                tag_format=self.tag_format,
            )

        return Version(
            dt.year,
            dt.month,
            0 if new_date else self.patch + 1,
            prerelease_token=self.prerelease_token,
            prerelease_revision=self.prerelease_revision,
            tag_format=self.tag_format,
        )


if __name__ == "__main__":
    with (
        mock.patch("semantic_release.version.version.Version", CalVersion),
        mock.patch("semantic_release.version.translator.Version", CalVersion),
        mock.patch(
            "semantic_release.version.declarations.pattern.Version", CalVersion
        ),
        mock.patch(
            "semantic_release.version.declarations.toml.Version", CalVersion
        ),
        mock.patch(
            "semantic_release.version.algorithm.DEFAULT_VERSION", "1000.1.0"
        ),
    ):
        main()
