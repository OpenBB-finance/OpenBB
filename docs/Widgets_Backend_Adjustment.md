# Widgets Adjustment on Backend Changes

## Overview
This fix ensures widgets in OpenBB can be dynamically adjusted when backend changes occur.

## Solution
- Refactored widget logic to listen for backend change events.
- Widgets now update and re-render automatically when the backend is switched.
- Improved state management for widget data sources.

## How to Use
- Switch backend as needed; widgets will adjust automatically.
- For custom widget logic, use the provided event hooks and update methods.

## Notes
- For troubleshooting, check widget event logs and backend status.
