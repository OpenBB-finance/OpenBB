"""Bank of Canada sub-package.

Hosts the BoC fetchers (``fx``, ``rates``, ``yields``) and the BoC
metadata loader. The fetcher classes themselves are added in Phase 5;
this file exists in Phase 1 so the package layout is stable and the
``import openbb_government_ca.boc`` resolves cleanly.
"""
