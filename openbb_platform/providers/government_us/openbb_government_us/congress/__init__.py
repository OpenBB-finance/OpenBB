"""Congress.gov Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_government_us.congress.models.amendment_info import (
    CongressAmendmentInfoFetcher,
)
from openbb_government_us.congress.models.amendment_text import (
    CongressAmendmentTextFetcher,
)
from openbb_government_us.congress.models.bill_info import CongressBillInfoFetcher
from openbb_government_us.congress.models.bill_text import CongressBillTextFetcher
from openbb_government_us.congress.models.congress_amendments import (
    CongressAmendmentsFetcher,
)
from openbb_government_us.congress.models.congress_bills import CongressBillsFetcher
from openbb_government_us.congress.models.congress_calendars import (
    CongressCalendarsFetcher,
)
from openbb_government_us.congress.models.congress_committee_documents import (
    CongressCommitteeDocumentsFetcher,
)
from openbb_government_us.congress.models.congress_committee_info import (
    CongressCommitteeInfoFetcher,
)
from openbb_government_us.congress.models.congress_laws import CongressLawsFetcher
from openbb_government_us.congress.models.congress_mandated_reports import (
    CongressMandatedReportsFetcher,
)
from openbb_government_us.congress.models.congress_members import CongressMembersFetcher
from openbb_government_us.congress.models.congress_search import CongressSearchFetcher
from openbb_government_us.congress.models.member_legislation import (
    CongressMemberLegislationFetcher,
)
from openbb_government_us.congress.models.member_votes import CongressMemberVotesFetcher

congress_gov_provider = Provider(
    name="congress_gov",
    website="https://www.govinfo.gov",
    description="""Legislative data from the U.S. Congress. Bills, bill metadata,
summaries, bill text, amendments, enacted laws, calendars, mandated reports, and
committees are all sourced from keyless public data (GovInfo bulk data, the
GovInfo link service, and the unitedstates dataset). No API key is required for
the 108th Congress onward; older Congresses predate the GovInfo bulk archives
and are served from the Congress.gov API, which needs a free API key.""",
    credentials=["api_key"],
    fetcher_dict={
        "CongressBills": CongressBillsFetcher,
        "CongressLaws": CongressLawsFetcher,
        "CongressCalendars": CongressCalendarsFetcher,
        "CongressMandatedReports": CongressMandatedReportsFetcher,
        "CongressBillInfo": CongressBillInfoFetcher,
        "CongressBillText": CongressBillTextFetcher,
        "CongressAmendments": CongressAmendmentsFetcher,
        "CongressAmendmentInfo": CongressAmendmentInfoFetcher,
        "CongressAmendmentText": CongressAmendmentTextFetcher,
        "CongressCommitteeInfo": CongressCommitteeInfoFetcher,
        "CongressCommitteeDocuments": CongressCommitteeDocumentsFetcher,
        "CongressSearch": CongressSearchFetcher,
        "CongressMembers": CongressMembersFetcher,
        "CongressMemberVotes": CongressMemberVotesFetcher,
        "CongressMemberLegislation": CongressMemberLegislationFetcher,
    },
    repr_name="Congress.gov",
    instructions="""Most endpoints use public, keyless data from GovInfo (bulk data
and the link service) and the unitedstates dataset, so no credentials are
required for the 108th Congress (2003) onward.

GovInfo does not publish bulk archives for earlier Congresses. Those requests
fall back to the Congress.gov API, which reaches back to the 93rd Congress
(1973) and requires an API key. Sign up for a free key at
https://api.congress.gov/sign-up/ and set it as 'congress_gov_api_key'.""",
)
