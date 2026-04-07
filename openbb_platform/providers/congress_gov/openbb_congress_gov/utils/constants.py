"""US Congress Constants."""

base_url = "https://api.congress.gov/v3/"

BillTypes: list = ["hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres"]

bill_type_options: list[dict[str, str]] = [
    {"label": "House Bill", "value": "hr"},
    {"label": "Senate Bill", "value": "s"},
    {"label": "House Joint Resolution", "value": "hjres"},
    {"label": "Senate Joint Resolution", "value": "sjres"},
    {"label": "House Concurrent Resolution", "value": "hconres"},
    {"label": "Senate Concurrent Resolution", "value": "sconres"},
    {"label": "House Simple Resolution", "value": "hres"},
    {"label": "Senate Simple Resolution", "value": "sres"},
]

bill_type_docstring = """Bill type (e.g., "hr" for House bills).

Must be one of: hr, s, hjres, sjres, hconres, sconres, hres, sres.

Bills
-----

A bill is the form used for most legislation, whether permanent or temporary, general or special, public or private.

A bill originating in the House of Representatives is designated by the letters “H.R.”,
signifying “House of Representatives”, followed by a number that it retains throughout all its parliamentary stages.

Bills are presented to the President for action when approved in identical form
by both the House of Representatives and the Senate.

Joint Resolutions
-----------------

Joint resolutions may originate either in the House of Representatives or in the Senate.

There is little practical difference between a bill and a joint resolution. Both are subject to the same procedure,
except for a joint resolution proposing an amendment to the Constitution.

On approval of such a resolution by two-thirds of both the House and Senate,
it is sent directly to the Administrator of General Services for submission to the individual states for ratification.

It is not presented to the President for approval.
A joint resolution originating in the House of Representatives is designated “H.J.Res.” followed by its individual number.
Joint resolutions become law in the same manner as bills.

Concurrent Resolutions
----------------------

Matters affecting the operations of both the House of Representatives and Senate
are usually initiated by means of concurrent resolutions.

A concurrent resolution originating in the House of Representatives is designated “H.Con.Res.”
followed by its individual number.

On approval by both the House of Representatives and Senate,
they are signed by the Clerk of the House and the Secretary of the Senate.

They are not presented to the President for action.

Simple Resolutions
------------------

A matter concerning the operation of either the House of Representatives or Senate
alone is initiated by a simple resolution.

A resolution affecting the House of Representatives is designated “H.Res.” followed by its number.

They are not presented to the President for action.

"""
LawTypes: list = ["pub", "priv"]

law_type_options: list[dict[str, str]] = [
    {"label": "Public Law", "value": "pub"},
    {"label": "Private Law", "value": "priv"},
]

law_type_docstring = """Law type filter.

Must be one of: pub, priv.

Public Laws
-----------

A public law is a law that affects the general public or classes of citizens.
It is identified by a number in the format "{congress}-{number}" (e.g., "119-44").

Private Laws
------------

A private law is a law that affects specific individuals, organizations, or localities
rather than the general public. Private laws are less common than public laws.

"""

AmendmentTypes: list = ["hamdt", "samdt", "suamdt"]

amendment_type_options: list[dict[str, str]] = [
    {"label": "House Amendment", "value": "hamdt"},
    {"label": "Senate Amendment", "value": "samdt"},
    {"label": "Senate Unamended", "value": "suamdt"},
]

amendment_type_docstring = """Amendment type (e.g., "hamdt" for House Amendments).

Must be one of:

- hamdt: An amendment offered or adopted in the House of Representatives.
House amendments are identified by "H.Amdt." followed by a number.
- samdt: An amendment offered or adopted in the Senate.
Senate amendments are identified by "S.Amdt." followed by a number.
- suamdt: A Senate amendment that was submitted but not subsequently amended.

"""

ChamberTypes: list = ["house", "senate", "joint"]

chamber_options: list[dict[str, str]] = [
    {"label": "House", "value": "house"},
    {"label": "Senate", "value": "senate"},
    {"label": "Joint", "value": "joint"},
]

doc_type_options: list[dict[str, str]] = [
    {"label": "All", "value": "all"},
    {"label": "Reports", "value": "report"},
    {"label": "Meetings & Hearings", "value": "meeting"},
    {"label": "Publications & Prints", "value": "publication"},
    {"label": "Legislation", "value": "legislation"},
]


COMMITTEES: dict[str, list[dict]] = {
    "senate": [
        {
            "label": "Senate Committee on Agriculture, Nutrition, and Forestry",
            "value": "ssaf00",
        },
        {"label": "Senate Committee on Appropriations", "value": "ssap00"},
        {"label": "Senate Committee on Armed Services", "value": "ssas00"},
        {
            "label": "Senate Committee on Banking, Housing, and Urban Affairs",
            "value": "ssbk00",
        },
        {
            "label": "Senate Committee on Commerce, Science, and Transportation",
            "value": "sscm00",
        },
        {
            "label": "Senate Committee on Energy and Natural Resources",
            "value": "sseg00",
        },
        {
            "label": "Senate Committee on Environment and Public Works",
            "value": "ssev00",
        },
        {"label": "Senate Committee on Finance", "value": "ssfi00"},
        {"label": "Senate Committee on Foreign Relations", "value": "ssfr00"},
        {
            "label": "Senate Committee on Health, Education, Labor, and Pensions",
            "value": "sshr00",
        },
        {
            "label": "Senate Committee on Homeland Security and Governmental Affairs",
            "value": "ssga00",
        },
        {"label": "Senate Committee on Indian Affairs", "value": "slia00"},
        {"label": "Senate Committee on Rules and Administration", "value": "ssra00"},
        {
            "label": "Senate Committee on Small Business and Entrepreneurship",
            "value": "sssb00",
        },
        {"label": "Senate Committee on Veterans' Affairs", "value": "ssva00"},
        {"label": "Senate Committee on the Budget", "value": "ssbu00"},
        {"label": "Senate Committee on the Judiciary", "value": "ssju00"},
        {"label": "Senate Select Committee on Ethics", "value": "slet00"},
        {"label": "Senate Select Committee on Intelligence", "value": "slin00"},
        {"label": "Senate Special Committee on Aging", "value": "spag00"},
        {
            "label": "United States Senate Caucus on International Narcotics Control",
            "value": "scnc00",
        },
    ],
    "house": [
        {"label": "House Committee on Agriculture", "value": "hsag00"},
        {"label": "House Committee on Appropriations", "value": "hsap00"},
        {"label": "House Committee on Armed Services", "value": "hsas00"},
        {"label": "House Committee on Education and Workforce", "value": "hsed00"},
        {"label": "House Committee on Energy and Commerce", "value": "hsif00"},
        {"label": "House Committee on Ethics", "value": "hsso00"},
        {"label": "House Committee on Financial Services", "value": "hsba00"},
        {"label": "House Committee on Foreign Affairs", "value": "hsfa00"},
        {"label": "House Committee on Homeland Security", "value": "hshm00"},
        {"label": "House Committee on House Administration", "value": "hsha00"},
        {"label": "House Committee on Natural Resources", "value": "hsii00"},
        {
            "label": "House Committee on Oversight and Government Reform",
            "value": "hsgo00",
        },
        {"label": "House Committee on Rules", "value": "hsru00"},
        {
            "label": "House Committee on Science, Space, and Technology",
            "value": "hssy00",
        },
        {"label": "House Committee on Small Business", "value": "hssm00"},
        {
            "label": "House Committee on Transportation and Infrastructure",
            "value": "hspw00",
        },
        {"label": "House Committee on Veterans' Affairs", "value": "hsvr00"},
        {"label": "House Committee on Ways and Means", "value": "hswm00"},
        {"label": "House Committee on the Budget", "value": "hsbu00"},
        {"label": "House Committee on the Judiciary", "value": "hsju00"},
        {
            "label": "House Permanent Select Committee on Intelligence",
            "value": "hlig00",
        },
    ],
    "joint": [
        {
            "label": "Commission on Security and Cooperation in Europe",
            "value": "jcse00",
        },
        {"label": "Joint Committee of Congress on the Library", "value": "jslc00"},
        {"label": "Joint Committee on Printing", "value": "jspr00"},
        {"label": "Joint Committee on Taxation", "value": "jstx00"},
        {"label": "Joint Economic Committee", "value": "jsec00"},
    ],
}

SUBCOMMITTEES: dict[str, list[dict]] = {
    "house/hsag00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Commodity Markets, Digital Assets, and Rural Development",
            "value": "hsag22",
        },
        {"label": "Conservation, Research, and Biotechnology", "value": "hsag14"},
        {"label": "Forestry and Horticulture", "value": "hsag15"},
        {
            "label": "General Farm Commodities, Risk Management, and Credit",
            "value": "hsag16",
        },
        {"label": "Livestock, Dairy, and Poultry", "value": "hsag29"},
        {"label": "Nutrition and Foreign Agriculture", "value": "hsag03"},
    ],
    "house/hsap00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Agriculture, Rural Development, Food and Drug Administration, and Related Agencies",
            "value": "hsap01",
        },
        {
            "label": "Commerce, Justice, Science, and Related Agencies",
            "value": "hsap19",
        },
        {"label": "Defense", "value": "hsap02"},
        {
            "label": "Energy and Water Development and Related Agencies",
            "value": "hsap10",
        },
        {"label": "Financial Services and General Government", "value": "hsap23"},
        {"label": "Homeland Security", "value": "hsap15"},
        {"label": "Interior, Environment, and Related Agencies", "value": "hsap06"},
        {
            "label": "Labor, Health and Human Services, Education, and Related Agencies",
            "value": "hsap07",
        },
        {"label": "Legislative Branch", "value": "hsap24"},
        {
            "label": "Military Construction, Veterans Affairs, and Related Agencies",
            "value": "hsap18",
        },
        {
            "label": "National Security, Department of State, and Related Programs",
            "value": "hsap04",
        },
        {
            "label": "Transportation, Housing and Urban Development, and Related Agencies",
            "value": "hsap20",
        },
    ],
    "house/hsas00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Cyber, Information Technologies, and Innovation", "value": "hsas35"},
        {"label": "Intelligence and Special Operations", "value": "hsas26"},
        {"label": "Military Personnel", "value": "hsas02"},
        {"label": "Readiness", "value": "hsas03"},
        {"label": "Seapower and Projection Forces", "value": "hsas28"},
        {"label": "Strategic Forces", "value": "hsas29"},
        {"label": "Tactical Air and Land Forces", "value": "hsas25"},
    ],
    "house/hsba00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Capital Markets", "value": "hsba16"},
        {
            "label": "Digital Assets, Financial Technology, and Artificial Intelligence",
            "value": "hsba21",
        },
        {"label": "Financial Institutions", "value": "hsba20"},
        {"label": "Housing and Insurance", "value": "hsba04"},
        {
            "label": "National Security, Illicit Finance, and International Financial Institutions",
            "value": "hsba10",
        },
        {"label": "Oversight and Investigations", "value": "hsba09"},
    ],
    "house/hsed00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Early Childhood, Elementary, and Secondary Education",
            "value": "hsed14",
        },
        {"label": "Health, Employment, Labor, and Pensions", "value": "hsed02"},
        {"label": "Higher Education and Workforce Development", "value": "hsed13"},
        {"label": "Workforce Protections", "value": "hsed10"},
    ],
    "house/hsfa00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Africa", "value": "hsfa16"},
        {"label": "East Asia and Pacific", "value": "hsfa05"},
        {"label": "Europe", "value": "hsfa14"},
        {"label": "Middle East and North Africa", "value": "hsfa13"},
        {"label": "Oversight and Intelligence", "value": "hsfa17"},
        {"label": "South and Central Asia", "value": "hsfa19"},
        {"label": "Western Hemisphere", "value": "hsfa07"},
    ],
    "house/hsgo00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Cybersecurity, Information Technology, and Government Innovation",
            "value": "hsgo12",
        },
        {"label": "Delivering on Government Efficiency", "value": "hsgo16"},
        {
            "label": "Economic Growth, Energy Policy, and Regulatory Affairs",
            "value": "hsgo05",
        },
        {"label": "Federal Law Enforcement", "value": "hsgo33"},
        {"label": "Government Operations", "value": "hsgo24"},
        {"label": "Health Care and Financial Services", "value": "hsgo27"},
        {"label": "Military and Foreign Affairs", "value": "hsgo06"},
    ],
    "house/hsha00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Elections", "value": "hsha08"},
        {"label": "Modernization and Innovation", "value": "hsha27"},
    ],
    "house/hshm00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Border Security and Enforcement", "value": "hshm11"},
        {"label": "Counterterrorism and Intelligence", "value": "hshm05"},
        {"label": "Cybersecurity and Infrastructure Protection", "value": "hshm08"},
        {"label": "Emergency Management and Technology", "value": "hshm12"},
        {"label": "Oversight, Investigations, and Accountability", "value": "hshm09"},
        {"label": "Transportation and Maritime Security", "value": "hshm07"},
    ],
    "house/hsif00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Commerce, Manufacturing, and Trade", "value": "hsif17"},
        {"label": "Communications and Technology", "value": "hsif16"},
        {"label": "Energy", "value": "hsif03"},
        {"label": "Environment", "value": "hsif18"},
        {"label": "Health", "value": "hsif14"},
        {"label": "Oversight and Investigations", "value": "hsif02"},
    ],
    "house/hsii00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Energy and Mineral Resources", "value": "hsii06"},
        {"label": "Federal Lands", "value": "hsii10"},
        {"label": "Indian and Insular Affairs", "value": "hsii24"},
        {"label": "Oversight and Investigations", "value": "hsii15"},
        {"label": "Water, Wildlife and Fisheries", "value": "hsii13"},
    ],
    "house/hlig00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Central Intelligence Agency", "value": "hlig01"},
        {"label": "Defense Intelligence and Overhead Architecture", "value": "hlig04"},
        {"label": "National Intelligence Enterprise", "value": "hlig06"},
        {"label": "National Security Agency and Cyber", "value": "hlig02"},
        {"label": "Open Source Intelligence", "value": "hlig11"},
        {"label": "Oversight and Investigations", "value": "hlig09"},
    ],
    "house/hsju00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Courts, Intellectual Property, Artificial Intelligence, and the Internet",
            "value": "hsju03",
        },
        {"label": "Crime and Federal Government Surveillance", "value": "hsju08"},
        {
            "label": "Immigration Integrity, Security, and Enforcement",
            "value": "hsju01",
        },
        {"label": "Oversight", "value": "hsju13"},
        {
            "label": "The Administrative State, Regulatory Reform, and Antitrust",
            "value": "hsju05",
        },
        {"label": "The Constitution and Limited Government", "value": "hsju10"},
    ],
    "house/hspw00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Aviation", "value": "hspw05"},
        {"label": "Coast Guard and Maritime Transportation", "value": "hspw07"},
        {
            "label": "Economic Development, Public Buildings, and Emergency Management",
            "value": "hspw13",
        },
        {"label": "Highways and Transit", "value": "hspw12"},
        {"label": "Railroads, Pipelines, and Hazardous Materials", "value": "hspw14"},
        {"label": "Water Resources and Environment", "value": "hspw02"},
    ],
    "house/hsru00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Legislative and Budget Process", "value": "hsru02"},
        {"label": "Rules and Organization of the House", "value": "hsru04"},
    ],
    "house/hssm00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Contracting and Infrastructure", "value": "hssm23"},
        {"label": "Economic Growth, Tax, and Capital Access", "value": "hssm27"},
        {
            "label": "Innovation, Entrepreneurship, and Workforce Development",
            "value": "hssm22",
        },
        {"label": "Oversight, Investigations, and Regulations", "value": "hssm24"},
        {"label": "Rural Development, Energy, and Supply Chains", "value": "hssm21"},
    ],
    "house/hssy00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Energy", "value": "hssy20"},
        {"label": "Environment", "value": "hssy18"},
        {"label": "Investigations and Oversight", "value": "hssy21"},
        {"label": "Research and Technology", "value": "hssy15"},
        {"label": "Space and Aeronautics", "value": "hssy16"},
    ],
    "house/hsvr00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Disability Assistance and Memorial Affairs", "value": "hsvr09"},
        {"label": "Economic Opportunity", "value": "hsvr10"},
        {"label": "Health", "value": "hsvr03"},
        {"label": "Oversight and Investigations", "value": "hsvr08"},
        {"label": "Technology Modernization", "value": "hsvr11"},
    ],
    "house/hswm00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Health", "value": "hswm02"},
        {"label": "Oversight", "value": "hswm06"},
        {"label": "Social Security", "value": "hswm01"},
        {"label": "Tax", "value": "hswm05"},
        {"label": "Trade", "value": "hswm04"},
        {"label": "Work and Welfare", "value": "hswm03"},
    ],
    "senate/ssaf00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Commodities, Derivatives, Risk Management, and Trade",
            "value": "ssaf13",
        },
        {
            "label": "Conservation, Forestry, Natural Resources, and Biotechnology",
            "value": "ssaf14",
        },
        {
            "label": "Food and Nutrition, Specialty Crops, Organics, and Research",
            "value": "ssaf16",
        },
        {"label": "Livestock, Dairy, Poultry, and Food Safety", "value": "ssaf17"},
        {"label": "Rural Development, Energy, and Credit", "value": "ssaf15"},
    ],
    "senate/ssap00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Agriculture, Rural Development, Food and Drug Administration, and Related Agencies",
            "value": "ssap01",
        },
        {
            "label": "Commerce, Justice, Science, and Related Agencies",
            "value": "ssap16",
        },
        {"label": "Department of Defense", "value": "ssap02"},
        {"label": "Department of Homeland Security", "value": "ssap14"},
        {
            "label": "Department of Interior, Environment, and Related Agencies",
            "value": "ssap17",
        },
        {
            "label": "Departments of Labor, Health and Human Services, and Education, and Related Agencies",
            "value": "ssap18",
        },
        {"label": "Energy and Water Development", "value": "ssap22"},
        {"label": "Financial Services and General Government", "value": "ssap23"},
        {"label": "Legislative Branch", "value": "ssap08"},
        {
            "label": "Military Construction, Veterans Affairs, and Related Agencies",
            "value": "ssap19",
        },
        {"label": "State, Foreign Operations, and Related Programs", "value": "ssap20"},
        {
            "label": "Transportation, Housing and Urban Development, and Related Agencies",
            "value": "ssap24",
        },
    ],
    "senate/ssas00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Airland", "value": "ssas14"},
        {"label": "Cybersecurity", "value": "ssas21"},
        {"label": "Emerging Threats and Capabilities", "value": "ssas20"},
        {"label": "Personnel", "value": "ssas17"},
        {"label": "Readiness and Management Support", "value": "ssas15"},
        {"label": "Seapower", "value": "ssas13"},
        {"label": "Strategic Forces", "value": "ssas16"},
    ],
    "senate/ssbk00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Digital Assets", "value": "ssbk13"},
        {"label": "Economic Policy", "value": "ssbk12"},
        {"label": "Financial Institutions and Consumer Protection", "value": "ssbk08"},
        {
            "label": "Housing, Transportation, and Community Development",
            "value": "ssbk09",
        },
        {
            "label": "National Security and International Trade and Finance",
            "value": "ssbk05",
        },
        {"label": "Securities, Insurance, and Investment", "value": "ssbk04"},
    ],
    "senate/sscm00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Aviation, Space, and Innovation", "value": "sscm33"},
        {"label": "Coast Guard, Maritime, and Fisheries", "value": "sscm36"},
        {
            "label": "Consumer Protection, Technology, and Data Privacy",
            "value": "sscm35",
        },
        {"label": "Science, Manufacturing, and Competitiveness", "value": "sscm37"},
        {
            "label": "Surface Transportation, Freight, Pipelines, and Safety",
            "value": "sscm38",
        },
        {"label": "Telecommunications and Media", "value": "sscm34"},
        {"label": "Tourism, Trade, and Export Promotion", "value": "sscm39"},
    ],
    "senate/sseg00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Energy", "value": "sseg01"},
        {"label": "National Parks", "value": "sseg04"},
        {"label": "Public Lands, Forests, and Mining", "value": "sseg03"},
        {"label": "Water and Power", "value": "sseg07"},
    ],
    "senate/ssev00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Chemical Safety, Waste Management, Environmental Justice, and Regulatory Oversight",
            "value": "ssev09",
        },
        {
            "label": "Clean Air, Climate, and Nuclear Innovation and Safety",
            "value": "ssev10",
        },
        {"label": "Fisheries, Wildlife, and Water", "value": "ssev15"},
        {"label": "Transportation and Infrastructure", "value": "ssev08"},
    ],
    "senate/ssfi00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Energy, Natural Resources, and Infrastructure", "value": "ssfi12"},
        {"label": "Fiscal Responsibility and Economic Growth", "value": "ssfi14"},
        {"label": "Health Care", "value": "ssfi10"},
        {
            "label": "International Trade, Customs, and Global Competitiveness",
            "value": "ssfi13",
        },
        {"label": "Social Security, Pensions, and Family Policy", "value": "ssfi02"},
        {"label": "Taxation and IRS Oversight", "value": "ssfi11"},
    ],
    "senate/ssfr00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Africa and Global Health Policy", "value": "ssfr09"},
        {
            "label": "East Asia, the Pacific, and International Cybersecurity Policy",
            "value": "ssfr02",
        },
        {"label": "Europe and Regional Security Cooperation", "value": "ssfr01"},
        {
            "label": (
                "Multilateral International Development, Multilateral Institutions,"
                " and International Economic, Energy, and Environmental Policy"
            ),
            "value": "ssfr15",
        },
        {
            "label": "Near East, South Asia, Central Asia, and Counterterrorism",
            "value": "ssfr07",
        },
        {
            "label": (
                "State Department and USAID Management, International Operations,"
                " and Bilateral International Development"
            ),
            "value": "ssfr14",
        },
        {
            "label": (
                "Western Hemisphere, Transnational Crime, Civilian Security,"
                " Democracy, Human Rights, and Global Women's Issues"
            ),
            "value": "ssfr06",
        },
    ],
    "senate/ssga00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Border Management, Federal Workforce, and Regulatory Affairs",
            "value": "ssga22",
        },
        {
            "label": "Disaster Management, District of Columbia, and Census",
            "value": "ssga20",
        },
        {"label": "Permanent Subcommittee on Investigations", "value": "ssga01"},
    ],
    "senate/sshr00": [
        {"label": "None (Parent Committee)", "value": ""},
        {"label": "Education and the American Family", "value": "sshr09"},
        {"label": "Employment and Workplace Safety", "value": "sshr11"},
        {"label": "Primary Health and Retirement Security", "value": "sshr12"},
    ],
    "senate/ssju00": [
        {"label": "None (Parent Committee)", "value": ""},
        {
            "label": "Antitrust, Competition Policy, and Consumer Rights",
            "value": "ssju01",
        },
        {"label": "Border Security and Immigration", "value": "ssju04"},
        {"label": "Crime and Counterterrorism", "value": "ssju22"},
        {
            "label": "Federal Courts, Oversight, Agency Action, and Federal Rights",
            "value": "ssju25",
        },
        {"label": "Human Rights and the Law", "value": "ssju27"},
        {"label": "Intellectual Property", "value": "ssju26"},
        {"label": "Privacy, Technology, and the Law", "value": "ssju28"},
        {"label": "the Constitution", "value": "ssju21"},
    ],
}
