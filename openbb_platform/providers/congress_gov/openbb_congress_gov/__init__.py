"""Congress.gov Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_congress_gov.models.amendment_info import CongressAmendmentInfoFetcher
from openbb_congress_gov.models.amendment_text import CongressAmendmentTextFetcher
from openbb_congress_gov.models.bill_info import CongressBillInfoFetcher
from openbb_congress_gov.models.bill_text import CongressBillTextFetcher
from openbb_congress_gov.models.congress_amendments import CongressAmendmentsFetcher
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.models.congress_calendars import CongressCalendarsFetcher
from openbb_congress_gov.models.congress_committee_documents import (
    CongressCommitteeDocumentsFetcher,
)
from openbb_congress_gov.models.congress_committee_info import (
    CongressCommitteeInfoFetcher,
)
from openbb_congress_gov.models.congress_laws import CongressLawsFetcher
from openbb_congress_gov.models.congress_mandated_reports import (
    CongressMandatedReportsFetcher,
)
from openbb_congress_gov.models.congress_members import CongressMembersFetcher
from openbb_congress_gov.models.congress_search import CongressSearchFetcher
from openbb_congress_gov.models.member_legislation import (
    CongressMemberLegislationFetcher,
)
from openbb_congress_gov.models.member_votes import CongressMemberVotesFetcher

congress_gov_provider = Provider(
    name="congress_gov",
    website="https://www.govinfo.gov",
    description="""Legislative data from the U.S. Congress. Bills, bill metadata,
summaries, bill text, amendments, enacted laws, calendars, mandated reports, and
committees are all sourced from keyless public data (GovInfo bulk data, the
GovInfo link service, and the unitedstates dataset). No API key is required.""",
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
    instructions="""All endpoints use public, keyless data from GovInfo (bulk data
and the link service) and the unitedstates dataset, so no credentials are
required.""",
)
