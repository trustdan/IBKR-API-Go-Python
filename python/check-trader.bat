@echo off
echo Running focused mypy checks on core trading modules...
echo.

echo Checking trader.py...
mypy --ignore-missing-imports --no-strict-optional python/src/app/trader.py

echo.
echo Checking scanner.py...
mypy --ignore-missing-imports --no-strict-optional python/src/app/scanner.py

echo.
echo Checking data_manager.py...
mypy --ignore-missing-imports --no-strict-optional --no-warn-return-any python/src/data/data_manager.py

echo.
echo Done with focused type checking.
