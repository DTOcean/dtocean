@ECHO OFF

REM Assumes sphinx, sphinx_rtd_theme and sphinxcontrib-versioning are installed
REM in the _sphinx conda environment

CALL activate _sphinx
sphinx-versioning build ^
                  -r experimental ^
                  . ^
                  _build\html ^
                  -- -D html_theme=sphinx_rtd_theme
