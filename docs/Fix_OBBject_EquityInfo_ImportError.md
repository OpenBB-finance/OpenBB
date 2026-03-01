# Fix ImportError: OBBject_EquityInfo

## Overview
This fix resolves the ImportError for `OBBject_EquityInfo` from `openbb_core.app.provider_interface` in OpenBB 4.5.0.

## Solution
- Ensured `OBBject_EquityInfo` is correctly exported in `provider_interface`.
- Updated import statements in affected modules to use the correct path.
- Verified that the symbol is available and importable in all relevant files.

## How to Use
- Update your code to import `OBBject_EquityInfo` from `openbb_core.app.provider_interface`.
- If you encounter further import errors, check for typos or outdated references.

## Notes
- For troubleshooting, see the module's documentation and error logs.
