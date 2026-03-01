# Automated Taxonomy Data Refresh via CI

## Overview
Taxonomy data in OpenBB should be refreshed regularly to ensure up-to-date information for analytics and reporting.

## Solution
A scheduled CI job has been implemented to automate the refresh of taxonomy data:
- The job runs nightly and pulls the latest taxonomy data from the designated source.
- Data is validated and updated in the OpenBB platform automatically.

## How to Use
- No manual action required; the CI job handles updates.
- For custom schedules, modify the CI configuration in `.github/workflows/taxonomy_refresh.yml`.

## Notes
- Monitor CI job status for any failures or interruptions.
- For troubleshooting, see logs in the CI dashboard.
