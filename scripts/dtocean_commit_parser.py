# The MIT License (MIT)

# Copyright (c) 2015 Rolf Erik Lekang
# Copyright (c) 2026 Mathew Topper

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from fnmatch import fnmatch
from logging import getLogger
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from re import DOTALL
from re import compile as regexp
from re import error as RegExpError
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Iterable,
    TypedDict,
)

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass
from semantic_release import CommitParser, LevelBump
from semantic_release.commit_parser import (
    ConventionalCommitParserOptions,
)
from semantic_release.commit_parser.conventional.parser import (
    ConventionalCommitParser,
)
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import force_str
from semantic_release.errors import InvalidParserOptions

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit


class FileFilter(TypedDict):
    selection_filters: list[str]
    ignore_filters: list[str]
    max_bump_level: LevelBump
    trigger_bump_level: LevelBump


@dataclass
class PathFilter:
    paths: Annotated[tuple[str, ...], Field(validate_default=True)] = (".",)
    max_bump_level: LevelBump = LevelBump.MAJOR
    trigger_bump_level: LevelBump = LevelBump.PATCH

    @field_validator("paths", mode="before")
    @classmethod
    def convert_strs_to_paths(cls, value: Any) -> tuple[str, ...]:
        if isinstance(value, str):
            return (value,)

        if isinstance(value, Path):
            return (str(value),)

        if isinstance(value, Iterable):
            results: list[str] = []
            for val in value:
                if isinstance(val, (str, Path)):
                    results.append(str(Path(val)))
                    continue

                msg = f"Invalid type: {type(val)}, expected str or Path."
                raise TypeError(msg)

            return tuple(results)

        msg = f"Invalid type: {type(value)}, expected str, Path, or Iterable."
        raise TypeError(msg)

    @field_validator("paths", mode="after")
    @classmethod
    def resolve_path(cls, dir_path_strs: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            (
                f"!{Path(str_path[1:]).expanduser().absolute().resolve()}"
                # maintains the negation prefix if it exists
                if str_path.startswith("!")
                # otherwise, resolve the path normally
                else str(Path(str_path).expanduser().absolute().resolve())
            )
            for str_path in dir_path_strs
        )


@dataclass
class DTOceanParserOptions(ConventionalCommitParserOptions):
    path_filters: dict[str, PathFilter] = Field(
        default_factory=lambda: {"default": PathFilter()}
    )
    scope_prefix: str = ""

    @field_validator("scope_prefix", mode="after")
    @classmethod
    def validate_scope_prefix(cls, scope_prefix: str) -> str:
        if not scope_prefix:
            return ""

        # Allow the special case of a plain wildcard although it's not a valid regex
        if scope_prefix == "*":
            return ".*"

        try:
            regexp(scope_prefix)
        except RegExpError as err:
            raise ValueError(f"Invalid regex {scope_prefix!r}") from err

        return scope_prefix


class DTOceanCommitParser(CommitParser[ParseResult, DTOceanParserOptions]):
    parser_options = DTOceanParserOptions

    def __init__(self, options: DTOceanParserOptions | None = None) -> None:
        super().__init__(options)

        try:
            commit_scope_pattern = regexp(
                r"\(" + self.options.scope_prefix + r"(?P<scope>[^\n]+)?\)",
            )
        except RegExpError as err:
            raise InvalidParserOptions(
                str.join(
                    "\n",
                    [
                        f"Invalid options for {self.__class__.__name__}",
                        "Unable to create regular expression from configured scope_prefix.",
                        "Please check the configured scope_prefix and remove or escape any regular expression characters.",
                    ],
                )
            ) from err

        try:
            commit_type_pattern = regexp(
                r"(?P<type>%s)" % str.join("|", self.options.allowed_tags)
            )
        except RegExpError as err:
            raise InvalidParserOptions(
                str.join(
                    "\n",
                    [
                        f"Invalid options for {self.__class__.__name__}",
                        "Unable to create regular expression from configured commit-types.",
                        "Please check the configured commit-types and remove or escape any regular expression characters.",
                    ],
                )
            ) from err

        # This regular expression includes scope prefix into the pattern and forces a scope to be present
        # PSR will match the full scope but we don't include it in the scope match,
        # which implicitly strips it from being included in the returned scope.
        self._strict_scope_pattern = regexp(
            str.join(
                "",
                [
                    r"^" + commit_type_pattern.pattern,
                    commit_scope_pattern.pattern,
                    r"(?P<break>!)?:\s+",
                    r"(?P<subject>[^\n]+)",
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=DOTALL,
        )

        self._optional_scope_pattern = regexp(
            str.join(
                "",
                [
                    r"^" + commit_type_pattern.pattern,
                    r"(?:\((?P<scope>[^\n]+)\))?",
                    r"(?P<break>!)?:\s+",
                    r"(?P<subject>[^\n]+)",
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=DOTALL,
        )

        self._file_filters: list[FileFilter] = (
            self._process_path_filter_options(self.options.path_filters)
        )
        self._logger = getLogger(
            str.join(
                ".",
                [
                    "semantic_release",
                    self.__module__,
                    self.__class__.__name__,
                ],
            )
        )

        self._base_parser = ConventionalCommitParser(
            options=ConventionalCommitParserOptions(
                **{
                    k: getattr(self.options, k)
                    for k in ConventionalCommitParserOptions().__dataclass_fields__
                }
            )
        )

    def get_default_options(self) -> DTOceanParserOptions:
        return DTOceanParserOptions()

    @staticmethod
    def _process_path_filter_options(  # noqa: C901
        path_filters: dict[str, PathFilter],
    ) -> list[FileFilter]:
        file_filters: list[FileFilter] = []

        for path_filter in path_filters.values():
            file_ignore_filters: list[str] = []
            file_selection_filters: list[str] = []
            unique_selection_filters: set[str] = set()
            unique_ignore_filters: set[str] = set()

            for str_path in path_filter.paths:
                str_filter = (
                    str_path[1:] if str_path.startswith("!") else str_path
                )
                filter_list = (
                    file_ignore_filters
                    if str_path.startswith("!")
                    else file_selection_filters
                )
                unique_cache = (
                    unique_ignore_filters
                    if str_path.startswith("!")
                    else unique_selection_filters
                )

                # Since fnmatch is not too flexible, we will expand the path filters to include the name and any subdirectories
                # as this is how gitignore is interpreted. Possible scenarios:
                # | Input      | Path Normalization | Filter List               |
                # | ---------- | ------------------ | ------------------------- |
                # | /          | /                  | /**                       | done
                # | /./        | /                  | /**                       | done
                # | /**        | /**                | /**                       | done
                # | /./**      | /**                | /**                       | done
                # | /*         | /*                 | /*                        | done
                # | .          | .                  | ./**                      | done
                # | ./         | .                  | ./**                      | done
                # | ././       | .                  | ./**                      | done
                # | ./**       | ./**               | ./**                      | done
                # | ./*        | ./*                | ./*                       | done
                # | ..         | ..                 | ../**                     | done
                # | ../        | ..                 | ../**                     | done
                # | ../**      | ../**              | ../**                     | done
                # | ../*       | ../*               | ../*                      | done
                # | ../..      | ../..              | ../../**                  | done
                # | ../../     | ../../             | ../../**                  | done
                # | ../../docs | ../../docs         | ../../docs, ../../docs/** | done
                # | src        | src                | src, src/**               | done
                # | src/       | src                | src/**                    | done
                # | src/*      | src/*              | src/*                     | done
                # | src/**     | src/**             | src/**                    | done
                # | /src       | /src               | /src, /src/**             | done
                # | /src/      | /src               | /src/**                   | done
                # | /src/**    | /src/**            | /src/**                   | done
                # | /src/*     | /src/*             | /src/*                    | done
                # | ../d/f.txt | ../d/f.txt         | ../d/f.txt, ../d/f.txt/** | done
                # This expansion will occur regardless of the negation prefix

                os_path: PurePath | PurePosixPath | PureWindowsPath = PurePath(
                    str_filter
                )

                if r"\\" in str_filter:
                    # Windows paths were given so we convert them to posix paths
                    os_path = PureWindowsPath(str_filter)
                    os_path = (
                        PureWindowsPath(
                            os_path.root, *os_path.parts[1:]
                        )  # drop any drive letter
                        if os_path.is_absolute()
                        else os_path
                    )
                    os_path = PurePosixPath(os_path.as_posix())

                path_normalized = str(os_path)
                if path_normalized == str(
                    Path(".").absolute().root
                ) or path_normalized == str(Path("/**")):
                    path_normalized = "/**"

                elif path_normalized == str(Path("/*")):
                    pass

                elif path_normalized == str(
                    Path(".")
                ) or path_normalized == str(Path("./**")):
                    path_normalized = "./**"

                elif path_normalized == str(Path("./*")):
                    path_normalized = "./*"

                elif path_normalized == str(
                    Path("..")
                ) or path_normalized == str(Path("../**")):
                    path_normalized = "../**"

                elif path_normalized == str(Path("../*")):
                    path_normalized = "../*"

                elif path_normalized.endswith(("..", "../**")):
                    path_normalized = f"{path_normalized.rstrip('*')}/**"

                elif str_filter.endswith(os.sep):
                    # If the path ends with a separator, it is a directory, so we add the directory and all subdirectories
                    path_normalized = f"{path_normalized}/**"

                elif not path_normalized.endswith("*"):
                    all_subdirs = f"{path_normalized}/**"
                    if all_subdirs not in unique_cache:
                        unique_cache.add(all_subdirs)
                        filter_list.append(all_subdirs)
                    # And fall through to add the path as is

                # END IF

                # Add the normalized path to the filter list if it is not already present
                if path_normalized not in unique_cache:
                    unique_cache.add(path_normalized)
                    filter_list.append(path_normalized)

            file_filter: FileFilter = {
                "selection_filters": file_selection_filters,
                "ignore_filters": file_ignore_filters,
                "max_bump_level": path_filter.max_bump_level,
                "trigger_bump_level": path_filter.trigger_bump_level,
            }
            file_filters.append(file_filter)

        return file_filters

    def logged_parse_error(self, commit: "Commit", error: str) -> ParseError:
        self._logger.debug(error)
        return ParseError(commit, error=error)

    def parse(self, commit: "Commit") -> ParseResult | list[ParseResult]:
        if (
            self.options.ignore_merge_commits
            and self._base_parser.is_merge_commit(commit)
        ):
            return self._base_parser.log_parse_error(
                commit, "Ignoring merge commit: %s" % commit.hexsha[:8]
            )

        separate_commits: list["Commit"] = (
            self._base_parser.unsquash_commit(commit)
            if self.options.parse_squash_commits
            else [commit]
        )

        # Parse each commit individually if there were more than one
        parsed_commits: list[ParseResult] = list(
            map(self.parse_commit, separate_commits)
        )

        def add_linked_merge_request(
            parsed_result: ParseResult, mr_number: str
        ) -> ParseResult:
            return (
                parsed_result
                if not isinstance(parsed_result, ParsedCommit)
                else ParsedCommit(
                    **{
                        **parsed_result._asdict(),
                        "linked_merge_request": mr_number,
                    }
                )
            )

        # TODO: improve this for other VCS systems other than GitHub & BitBucket
        # Github works as the first commit in a squash merge commit has the PR number
        # appended to the first line of the commit message
        lead_commit = next(iter(parsed_commits))

        if (
            isinstance(lead_commit, ParsedCommit)
            and lead_commit.linked_merge_request
        ):
            # If the first commit has linked merge requests, assume all commits
            # are part of the same PR and add the linked merge requests to all
            # parsed commits
            parsed_commits = [
                lead_commit,
                *map(
                    lambda parsed_result, mr=lead_commit.linked_merge_request: (  # type: ignore[misc]
                        add_linked_merge_request(parsed_result, mr)
                    ),
                    parsed_commits[1:],
                ),
            ]

        elif isinstance(lead_commit, ParseError) and (
            mr_match := self._base_parser.mr_selector.search(
                force_str(lead_commit.message)
            )
        ):
            # Handle BitBucket Squash Merge Commits (see #1085), which have non angular commit
            # format but include the PR number in the commit subject that we want to extract
            linked_merge_request = mr_match.group("mr_number")

            # apply the linked MR to all commits
            parsed_commits = [
                add_linked_merge_request(parsed_result, linked_merge_request)
                for parsed_result in parsed_commits
            ]

        return parsed_commits

    def parse_message(
        self, message: str, strict_scope: bool = False
    ) -> ParsedMessageResult | None:
        if (
            not (parsed_match := self._strict_scope_pattern.match(message))
            and strict_scope
        ):
            return None

        if not parsed_match and not (
            parsed_match := self._optional_scope_pattern.match(message)
        ):
            return None

        return self._base_parser.create_parsed_message_result(parsed_match)

    def parse_commit(self, commit: "Commit") -> ParseResult:
        """Attempt to parse the commit message with a regular expression into a ParseResult."""
        # Multiple scenarios to consider when parsing a commit message [Truth table]:
        # =======================================================================================================
        # |    ||                         INPUTS                         ||                                     |
        # |  # ||------------------------+----------------+--------------||                Result               |
        # |    || Example Commit Message | Relevant Files | Scope Prefix ||                                     |
        # |----||------------------------+----------------+--------------||-------------------------------------|
        # |  1 || type(prefix-cli): msg  |            yes |    "prefix-" ||                        ParsedCommit |
        # |  2 || type(prefix-cli): msg  |            yes |           "" ||                        ParsedCommit |
        # |  3 || type(prefix-cli): msg  |             no |    "prefix-" ||                        ParsedCommit |
        # |  4 || type(prefix-cli): msg  |             no |           "" ||                ParseError[No files] |
        # |  5 || type(scope-cli): msg   |            yes |    "prefix-" ||                        ParsedCommit |
        # |  6 || type(scope-cli): msg   |            yes |           "" ||                        ParsedCommit |
        # |  7 || type(scope-cli): msg   |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # |  8 || type(scope-cli): msg   |             no |           "" ||                ParseError[No files] |
        # |  9 || type(cli): msg         |            yes |    "prefix-" ||                        ParsedCommit |
        # | 10 || type(cli): msg         |            yes |           "" ||                        ParsedCommit |
        # | 11 || type(cli): msg         |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # | 12 || type(cli): msg         |             no |           "" ||                ParseError[No files] |
        # | 13 || type: msg              |            yes |    "prefix-" ||                        ParsedCommit |
        # | 14 || type: msg              |            yes |           "" ||                        ParsedCommit |
        # | 15 || type: msg              |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # | 16 || type: msg              |             no |           "" ||                ParseError[No files] |
        # | 17 || non-conventional msg   |            yes |    "prefix-" ||          ParseError[Invalid Syntax] |
        # | 18 || non-conventional msg   |            yes |           "" ||          ParseError[Invalid Syntax] |
        # | 19 || non-conventional msg   |             no |    "prefix-" ||          ParseError[Invalid Syntax] |
        # | 20 || non-conventional msg   |             no |           "" ||          ParseError[Invalid Syntax] |
        # =======================================================================================================

        # Initial Logic Flow:
        # [1] When there are no relevant files and a scope prefix is defined, we enforce a strict scope
        # [2] When there are no relevant files and no scope prefix is defined, we parse scoped or unscoped commits
        # [3] When there are relevant files, we parse scoped or unscoped commits regardless of any defined prefix
        (
            has_relevant_changed_files,
            max_bump,
            trigger_bump,
        ) = self._has_relevant_changed_files(commit)
        strict_scope = bool(
            not has_relevant_changed_files and self.options.scope_prefix
        )
        pmsg_result = self.parse_message(
            message=force_str(commit.message),
            strict_scope=strict_scope,
        )

        if pmsg_result and pmsg_result.bump < trigger_bump:
            return self.logged_parse_error(
                commit,
                (
                    f"Bump level {pmsg_result.bump.value} of commit {commit.hexsha[:7]} "
                    f"does not meet trigger level of {trigger_bump.value}"
                ),
            )

        # Force the bump level to maximum is set
        if pmsg_result is not None and pmsg_result.bump > max_bump:
            pmsg_result = ParsedMessageResult(
                bump=max_bump,
                type=pmsg_result.type,
                category=pmsg_result.category,
                scope=pmsg_result.scope,
                descriptions=pmsg_result.descriptions,
                breaking_descriptions=pmsg_result.breaking_descriptions,
                release_notices=pmsg_result.release_notices,
                linked_issues=pmsg_result.linked_issues,
                linked_merge_request=pmsg_result.linked_merge_request,
            )

        if pmsg_result and (has_relevant_changed_files or strict_scope):
            self._logger.debug(
                "commit %s introduces a %s level_bump",
                commit.hexsha[:8],
                pmsg_result.bump,
            )

            return ParsedCommit.from_parsed_message_result(commit, pmsg_result)

        if pmsg_result and not has_relevant_changed_files:
            return self.logged_parse_error(
                commit,
                f"Commit {commit.hexsha[:7]} has no changed files matching the path filter(s)",
            )

        if strict_scope and self.parse_message(
            str(commit.message), strict_scope=False
        ):
            return self.logged_parse_error(
                commit,
                str.join(
                    " and ",
                    [
                        f"Commit {commit.hexsha[:7]} has no changed files matching the path filter(s)",
                        f"the scope does not match scope prefix '{self.options.scope_prefix}'",
                    ],
                ),
            )

        return self.logged_parse_error(
            commit,
            f"Format Mismatch! Unable to parse commit message: {commit.message!r}",
        )

    def unsquash_commit_message(self, message: str) -> list[str]:
        return self._base_parser.unsquash_commit_message(message)

    def _has_relevant_changed_files(
        self, commit: "Commit"
    ) -> tuple[bool, LevelBump, LevelBump]:
        # Extract git root from commit
        git_root = (
            Path(commit.repo.working_tree_dir or commit.repo.working_dir)
            .absolute()
            .resolve()
        )

        cwd = Path.cwd().absolute().resolve()

        rel_cwd = (
            cwd.relative_to(git_root) if git_root in cwd.parents else Path(".")
        )

        is_relevant = False
        max_bump_levels: list[LevelBump] = []
        trigger_bump_levels: list[LevelBump] = []

        for file_filter in self._file_filters:
            sandboxed_selection_filters: list[str] = [
                str(file_filter)
                for file_filter in (
                    (
                        git_root / select_filter.rstrip("/")
                        if Path(select_filter).is_absolute()
                        else git_root / rel_cwd / select_filter
                    )
                    for select_filter in file_filter["selection_filters"]
                )
                if git_root in file_filter.parents
            ]

            sandboxed_ignore_filters: list[str] = [
                str(file_filter)
                for file_filter in (
                    (
                        git_root / ignore_filter.rstrip("/")
                        if Path(ignore_filter).is_absolute()
                        else git_root / rel_cwd / ignore_filter
                    )
                    for ignore_filter in file_filter["ignore_filters"]
                )
                if git_root in file_filter.parents
            ]

            # Check if the changed files of the commit that match the path filters
            for full_path in iter(
                str(git_root / rel_git_path)
                for rel_git_path in commit.stats.files
            ):
                # Check if the filepath matches any of the file selection filters
                if not any(
                    fnmatch(full_path, select_filter)
                    for select_filter in sandboxed_selection_filters
                ):
                    continue

                # Pass filter matches, so now evaluate if it is supposed to be ignored
                if not any(
                    fnmatch(full_path, ignore_filter)
                    for ignore_filter in sandboxed_ignore_filters
                ):
                    # No ignore filter matched, so it must be a relevant file
                    is_relevant |= True
                    max_bump_levels.append(file_filter["max_bump_level"])
                    trigger_bump_levels.append(
                        file_filter["trigger_bump_level"]
                    )

        if not max_bump_levels:
            max_bump_level = LevelBump.MAJOR
        else:
            max_bump_level = max(max_bump_levels)

        if not trigger_bump_levels:
            trigger_bump_level = LevelBump.NO_RELEASE
        else:
            trigger_bump_level = min(trigger_bump_levels)

        return is_relevant, max_bump_level, trigger_bump_level
