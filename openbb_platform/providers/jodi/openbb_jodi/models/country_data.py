"""JODI Country Series Data Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class JodiCountryData(Data):
    """JODI Country Series Data.

    One column per reporting country, in alphabetical order. Countries
    without an observation for the period and measure are None.
    """

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    albania: float | None = Field(
        default=None,
        description="Monthly value reported by Albania.",
        json_schema_extra={"x-widget_config": {"headerName": "Albania"}},
    )
    algeria: float | None = Field(
        default=None,
        description="Monthly value reported by Algeria.",
        json_schema_extra={"x-widget_config": {"headerName": "Algeria"}},
    )
    angola: float | None = Field(
        default=None,
        description="Monthly value reported by Angola.",
        json_schema_extra={"x-widget_config": {"headerName": "Angola"}},
    )
    argentina: float | None = Field(
        default=None,
        description="Monthly value reported by Argentina.",
        json_schema_extra={"x-widget_config": {"headerName": "Argentina"}},
    )
    armenia: float | None = Field(
        default=None,
        description="Monthly value reported by Armenia.",
        json_schema_extra={"x-widget_config": {"headerName": "Armenia"}},
    )
    australia: float | None = Field(
        default=None,
        description="Monthly value reported by Australia.",
        json_schema_extra={"x-widget_config": {"headerName": "Australia"}},
    )
    austria: float | None = Field(
        default=None,
        description="Monthly value reported by Austria.",
        json_schema_extra={"x-widget_config": {"headerName": "Austria"}},
    )
    azerbaijan: float | None = Field(
        default=None,
        description="Monthly value reported by Azerbaijan.",
        json_schema_extra={"x-widget_config": {"headerName": "Azerbaijan"}},
    )
    bahrain: float | None = Field(
        default=None,
        description="Monthly value reported by Bahrain.",
        json_schema_extra={"x-widget_config": {"headerName": "Bahrain"}},
    )
    bangladesh: float | None = Field(
        default=None,
        description="Monthly value reported by Bangladesh.",
        json_schema_extra={"x-widget_config": {"headerName": "Bangladesh"}},
    )
    barbados: float | None = Field(
        default=None,
        description="Monthly value reported by Barbados.",
        json_schema_extra={"x-widget_config": {"headerName": "Barbados"}},
    )
    belarus: float | None = Field(
        default=None,
        description="Monthly value reported by Belarus.",
        json_schema_extra={"x-widget_config": {"headerName": "Belarus"}},
    )
    belgium: float | None = Field(
        default=None,
        description="Monthly value reported by Belgium.",
        json_schema_extra={"x-widget_config": {"headerName": "Belgium"}},
    )
    belize: float | None = Field(
        default=None,
        description="Monthly value reported by Belize.",
        json_schema_extra={"x-widget_config": {"headerName": "Belize"}},
    )
    bermuda: float | None = Field(
        default=None,
        description="Monthly value reported by Bermuda.",
        json_schema_extra={"x-widget_config": {"headerName": "Bermuda"}},
    )
    bolivia: float | None = Field(
        default=None,
        description="Monthly value reported by Bolivia.",
        json_schema_extra={"x-widget_config": {"headerName": "Bolivia"}},
    )
    brazil: float | None = Field(
        default=None,
        description="Monthly value reported by Brazil.",
        json_schema_extra={"x-widget_config": {"headerName": "Brazil"}},
    )
    brunei: float | None = Field(
        default=None,
        description="Monthly value reported by Brunei.",
        json_schema_extra={"x-widget_config": {"headerName": "Brunei"}},
    )
    bulgaria: float | None = Field(
        default=None,
        description="Monthly value reported by Bulgaria.",
        json_schema_extra={"x-widget_config": {"headerName": "Bulgaria"}},
    )
    canada: float | None = Field(
        default=None,
        description="Monthly value reported by Canada.",
        json_schema_extra={"x-widget_config": {"headerName": "Canada"}},
    )
    chile: float | None = Field(
        default=None,
        description="Monthly value reported by Chile.",
        json_schema_extra={"x-widget_config": {"headerName": "Chile"}},
    )
    china: float | None = Field(
        default=None,
        description="Monthly value reported by China.",
        json_schema_extra={"x-widget_config": {"headerName": "China"}},
    )
    colombia: float | None = Field(
        default=None,
        description="Monthly value reported by Colombia.",
        json_schema_extra={"x-widget_config": {"headerName": "Colombia"}},
    )
    costa_rica: float | None = Field(
        default=None,
        description="Monthly value reported by Costa Rica.",
        json_schema_extra={"x-widget_config": {"headerName": "Costa Rica"}},
    )
    croatia: float | None = Field(
        default=None,
        description="Monthly value reported by Croatia.",
        json_schema_extra={"x-widget_config": {"headerName": "Croatia"}},
    )
    cuba: float | None = Field(
        default=None,
        description="Monthly value reported by Cuba.",
        json_schema_extra={"x-widget_config": {"headerName": "Cuba"}},
    )
    cyprus: float | None = Field(
        default=None,
        description="Monthly value reported by Cyprus.",
        json_schema_extra={"x-widget_config": {"headerName": "Cyprus"}},
    )
    czechia: float | None = Field(
        default=None,
        description="Monthly value reported by Czechia.",
        json_schema_extra={"x-widget_config": {"headerName": "Czechia"}},
    )
    denmark: float | None = Field(
        default=None,
        description="Monthly value reported by Denmark.",
        json_schema_extra={"x-widget_config": {"headerName": "Denmark"}},
    )
    dominican_republic: float | None = Field(
        default=None,
        description="Monthly value reported by Dominican Republic.",
        json_schema_extra={"x-widget_config": {"headerName": "Dominican Republic"}},
    )
    ecuador: float | None = Field(
        default=None,
        description="Monthly value reported by Ecuador.",
        json_schema_extra={"x-widget_config": {"headerName": "Ecuador"}},
    )
    egypt: float | None = Field(
        default=None,
        description="Monthly value reported by Egypt.",
        json_schema_extra={"x-widget_config": {"headerName": "Egypt"}},
    )
    el_salvador: float | None = Field(
        default=None,
        description="Monthly value reported by El Salvador.",
        json_schema_extra={"x-widget_config": {"headerName": "El Salvador"}},
    )
    equatorial_guinea: float | None = Field(
        default=None,
        description="Monthly value reported by Equatorial Guinea.",
        json_schema_extra={"x-widget_config": {"headerName": "Equatorial Guinea"}},
    )
    estonia: float | None = Field(
        default=None,
        description="Monthly value reported by Estonia.",
        json_schema_extra={"x-widget_config": {"headerName": "Estonia"}},
    )
    eswatini: float | None = Field(
        default=None,
        description="Monthly value reported by Eswatini.",
        json_schema_extra={"x-widget_config": {"headerName": "Eswatini"}},
    )
    finland: float | None = Field(
        default=None,
        description="Monthly value reported by Finland.",
        json_schema_extra={"x-widget_config": {"headerName": "Finland"}},
    )
    france: float | None = Field(
        default=None,
        description="Monthly value reported by France.",
        json_schema_extra={"x-widget_config": {"headerName": "France"}},
    )
    gabon: float | None = Field(
        default=None,
        description="Monthly value reported by Gabon.",
        json_schema_extra={"x-widget_config": {"headerName": "Gabon"}},
    )
    gambia: float | None = Field(
        default=None,
        description="Monthly value reported by Gambia.",
        json_schema_extra={"x-widget_config": {"headerName": "Gambia"}},
    )
    georgia: float | None = Field(
        default=None,
        description="Monthly value reported by Georgia.",
        json_schema_extra={"x-widget_config": {"headerName": "Georgia"}},
    )
    germany: float | None = Field(
        default=None,
        description="Monthly value reported by Germany.",
        json_schema_extra={"x-widget_config": {"headerName": "Germany"}},
    )
    greece: float | None = Field(
        default=None,
        description="Monthly value reported by Greece.",
        json_schema_extra={"x-widget_config": {"headerName": "Greece"}},
    )
    grenada: float | None = Field(
        default=None,
        description="Monthly value reported by Grenada.",
        json_schema_extra={"x-widget_config": {"headerName": "Grenada"}},
    )
    guatemala: float | None = Field(
        default=None,
        description="Monthly value reported by Guatemala.",
        json_schema_extra={"x-widget_config": {"headerName": "Guatemala"}},
    )
    guyana: float | None = Field(
        default=None,
        description="Monthly value reported by Guyana.",
        json_schema_extra={"x-widget_config": {"headerName": "Guyana"}},
    )
    haiti: float | None = Field(
        default=None,
        description="Monthly value reported by Haiti.",
        json_schema_extra={"x-widget_config": {"headerName": "Haiti"}},
    )
    honduras: float | None = Field(
        default=None,
        description="Monthly value reported by Honduras.",
        json_schema_extra={"x-widget_config": {"headerName": "Honduras"}},
    )
    hong_kong: float | None = Field(
        default=None,
        description="Monthly value reported by Hong Kong.",
        json_schema_extra={"x-widget_config": {"headerName": "Hong Kong"}},
    )
    hungary: float | None = Field(
        default=None,
        description="Monthly value reported by Hungary.",
        json_schema_extra={"x-widget_config": {"headerName": "Hungary"}},
    )
    iceland: float | None = Field(
        default=None,
        description="Monthly value reported by Iceland.",
        json_schema_extra={"x-widget_config": {"headerName": "Iceland"}},
    )
    india: float | None = Field(
        default=None,
        description="Monthly value reported by India.",
        json_schema_extra={"x-widget_config": {"headerName": "India"}},
    )
    indonesia: float | None = Field(
        default=None,
        description="Monthly value reported by Indonesia.",
        json_schema_extra={"x-widget_config": {"headerName": "Indonesia"}},
    )
    iran: float | None = Field(
        default=None,
        description="Monthly value reported by Iran.",
        json_schema_extra={"x-widget_config": {"headerName": "Iran"}},
    )
    iraq: float | None = Field(
        default=None,
        description="Monthly value reported by Iraq.",
        json_schema_extra={"x-widget_config": {"headerName": "Iraq"}},
    )
    ireland: float | None = Field(
        default=None,
        description="Monthly value reported by Ireland.",
        json_schema_extra={"x-widget_config": {"headerName": "Ireland"}},
    )
    italy: float | None = Field(
        default=None,
        description="Monthly value reported by Italy.",
        json_schema_extra={"x-widget_config": {"headerName": "Italy"}},
    )
    jamaica: float | None = Field(
        default=None,
        description="Monthly value reported by Jamaica.",
        json_schema_extra={"x-widget_config": {"headerName": "Jamaica"}},
    )
    japan: float | None = Field(
        default=None,
        description="Monthly value reported by Japan.",
        json_schema_extra={"x-widget_config": {"headerName": "Japan"}},
    )
    kazakhstan: float | None = Field(
        default=None,
        description="Monthly value reported by Kazakhstan.",
        json_schema_extra={"x-widget_config": {"headerName": "Kazakhstan"}},
    )
    kuwait: float | None = Field(
        default=None,
        description="Monthly value reported by Kuwait.",
        json_schema_extra={"x-widget_config": {"headerName": "Kuwait"}},
    )
    latvia: float | None = Field(
        default=None,
        description="Monthly value reported by Latvia.",
        json_schema_extra={"x-widget_config": {"headerName": "Latvia"}},
    )
    libya: float | None = Field(
        default=None,
        description="Monthly value reported by Libya.",
        json_schema_extra={"x-widget_config": {"headerName": "Libya"}},
    )
    lithuania: float | None = Field(
        default=None,
        description="Monthly value reported by Lithuania.",
        json_schema_extra={"x-widget_config": {"headerName": "Lithuania"}},
    )
    luxembourg: float | None = Field(
        default=None,
        description="Monthly value reported by Luxembourg.",
        json_schema_extra={"x-widget_config": {"headerName": "Luxembourg"}},
    )
    malaysia: float | None = Field(
        default=None,
        description="Monthly value reported by Malaysia.",
        json_schema_extra={"x-widget_config": {"headerName": "Malaysia"}},
    )
    malta: float | None = Field(
        default=None,
        description="Monthly value reported by Malta.",
        json_schema_extra={"x-widget_config": {"headerName": "Malta"}},
    )
    mauritius: float | None = Field(
        default=None,
        description="Monthly value reported by Mauritius.",
        json_schema_extra={"x-widget_config": {"headerName": "Mauritius"}},
    )
    mexico: float | None = Field(
        default=None,
        description="Monthly value reported by Mexico.",
        json_schema_extra={"x-widget_config": {"headerName": "Mexico"}},
    )
    moldova: float | None = Field(
        default=None,
        description="Monthly value reported by Moldova.",
        json_schema_extra={"x-widget_config": {"headerName": "Moldova"}},
    )
    morocco: float | None = Field(
        default=None,
        description="Monthly value reported by Morocco.",
        json_schema_extra={"x-widget_config": {"headerName": "Morocco"}},
    )
    myanmar: float | None = Field(
        default=None,
        description="Monthly value reported by Myanmar.",
        json_schema_extra={"x-widget_config": {"headerName": "Myanmar"}},
    )
    nepal: float | None = Field(
        default=None,
        description="Monthly value reported by Nepal.",
        json_schema_extra={"x-widget_config": {"headerName": "Nepal"}},
    )
    netherlands: float | None = Field(
        default=None,
        description="Monthly value reported by Netherlands.",
        json_schema_extra={"x-widget_config": {"headerName": "Netherlands"}},
    )
    new_zealand: float | None = Field(
        default=None,
        description="Monthly value reported by New Zealand.",
        json_schema_extra={"x-widget_config": {"headerName": "New Zealand"}},
    )
    nicaragua: float | None = Field(
        default=None,
        description="Monthly value reported by Nicaragua.",
        json_schema_extra={"x-widget_config": {"headerName": "Nicaragua"}},
    )
    niger: float | None = Field(
        default=None,
        description="Monthly value reported by Niger.",
        json_schema_extra={"x-widget_config": {"headerName": "Niger"}},
    )
    nigeria: float | None = Field(
        default=None,
        description="Monthly value reported by Nigeria.",
        json_schema_extra={"x-widget_config": {"headerName": "Nigeria"}},
    )
    north_macedonia: float | None = Field(
        default=None,
        description="Monthly value reported by North Macedonia.",
        json_schema_extra={"x-widget_config": {"headerName": "North Macedonia"}},
    )
    norway: float | None = Field(
        default=None,
        description="Monthly value reported by Norway.",
        json_schema_extra={"x-widget_config": {"headerName": "Norway"}},
    )
    oman: float | None = Field(
        default=None,
        description="Monthly value reported by Oman.",
        json_schema_extra={"x-widget_config": {"headerName": "Oman"}},
    )
    panama: float | None = Field(
        default=None,
        description="Monthly value reported by Panama.",
        json_schema_extra={"x-widget_config": {"headerName": "Panama"}},
    )
    papua_new_guinea: float | None = Field(
        default=None,
        description="Monthly value reported by Papua New Guinea.",
        json_schema_extra={"x-widget_config": {"headerName": "Papua New Guinea"}},
    )
    paraguay: float | None = Field(
        default=None,
        description="Monthly value reported by Paraguay.",
        json_schema_extra={"x-widget_config": {"headerName": "Paraguay"}},
    )
    peru: float | None = Field(
        default=None,
        description="Monthly value reported by Peru.",
        json_schema_extra={"x-widget_config": {"headerName": "Peru"}},
    )
    philippines: float | None = Field(
        default=None,
        description="Monthly value reported by Philippines.",
        json_schema_extra={"x-widget_config": {"headerName": "Philippines"}},
    )
    poland: float | None = Field(
        default=None,
        description="Monthly value reported by Poland.",
        json_schema_extra={"x-widget_config": {"headerName": "Poland"}},
    )
    portugal: float | None = Field(
        default=None,
        description="Monthly value reported by Portugal.",
        json_schema_extra={"x-widget_config": {"headerName": "Portugal"}},
    )
    qatar: float | None = Field(
        default=None,
        description="Monthly value reported by Qatar.",
        json_schema_extra={"x-widget_config": {"headerName": "Qatar"}},
    )
    romania: float | None = Field(
        default=None,
        description="Monthly value reported by Romania.",
        json_schema_extra={"x-widget_config": {"headerName": "Romania"}},
    )
    russia: float | None = Field(
        default=None,
        description="Monthly value reported by Russia.",
        json_schema_extra={"x-widget_config": {"headerName": "Russia"}},
    )
    saudi_arabia: float | None = Field(
        default=None,
        description="Monthly value reported by Saudi Arabia.",
        json_schema_extra={"x-widget_config": {"headerName": "Saudi Arabia"}},
    )
    serbia: float | None = Field(
        default=None,
        description="Monthly value reported by Serbia.",
        json_schema_extra={"x-widget_config": {"headerName": "Serbia"}},
    )
    singapore: float | None = Field(
        default=None,
        description="Monthly value reported by Singapore.",
        json_schema_extra={"x-widget_config": {"headerName": "Singapore"}},
    )
    slovakia: float | None = Field(
        default=None,
        description="Monthly value reported by Slovakia.",
        json_schema_extra={"x-widget_config": {"headerName": "Slovakia"}},
    )
    slovenia: float | None = Field(
        default=None,
        description="Monthly value reported by Slovenia.",
        json_schema_extra={"x-widget_config": {"headerName": "Slovenia"}},
    )
    south_africa: float | None = Field(
        default=None,
        description="Monthly value reported by South Africa.",
        json_schema_extra={"x-widget_config": {"headerName": "South Africa"}},
    )
    south_korea: float | None = Field(
        default=None,
        description="Monthly value reported by South Korea.",
        json_schema_extra={"x-widget_config": {"headerName": "South Korea"}},
    )
    spain: float | None = Field(
        default=None,
        description="Monthly value reported by Spain.",
        json_schema_extra={"x-widget_config": {"headerName": "Spain"}},
    )
    sudan: float | None = Field(
        default=None,
        description="Monthly value reported by Sudan.",
        json_schema_extra={"x-widget_config": {"headerName": "Sudan"}},
    )
    suriname: float | None = Field(
        default=None,
        description="Monthly value reported by Suriname.",
        json_schema_extra={"x-widget_config": {"headerName": "Suriname"}},
    )
    sweden: float | None = Field(
        default=None,
        description="Monthly value reported by Sweden.",
        json_schema_extra={"x-widget_config": {"headerName": "Sweden"}},
    )
    switzerland: float | None = Field(
        default=None,
        description="Monthly value reported by Switzerland.",
        json_schema_extra={"x-widget_config": {"headerName": "Switzerland"}},
    )
    syria: float | None = Field(
        default=None,
        description="Monthly value reported by Syria.",
        json_schema_extra={"x-widget_config": {"headerName": "Syria"}},
    )
    taiwan: float | None = Field(
        default=None,
        description="Monthly value reported by Taiwan.",
        json_schema_extra={"x-widget_config": {"headerName": "Taiwan"}},
    )
    tajikistan: float | None = Field(
        default=None,
        description="Monthly value reported by Tajikistan.",
        json_schema_extra={"x-widget_config": {"headerName": "Tajikistan"}},
    )
    thailand: float | None = Field(
        default=None,
        description="Monthly value reported by Thailand.",
        json_schema_extra={"x-widget_config": {"headerName": "Thailand"}},
    )
    trinidad_and_tobago: float | None = Field(
        default=None,
        description="Monthly value reported by Trinidad and Tobago.",
        json_schema_extra={"x-widget_config": {"headerName": "Trinidad and Tobago"}},
    )
    tunisia: float | None = Field(
        default=None,
        description="Monthly value reported by Tunisia.",
        json_schema_extra={"x-widget_config": {"headerName": "Tunisia"}},
    )
    turkiye: float | None = Field(
        default=None,
        description="Monthly value reported by Turkiye.",
        json_schema_extra={"x-widget_config": {"headerName": "Turkiye"}},
    )
    ukraine: float | None = Field(
        default=None,
        description="Monthly value reported by Ukraine.",
        json_schema_extra={"x-widget_config": {"headerName": "Ukraine"}},
    )
    united_arab_emirates: float | None = Field(
        default=None,
        description="Monthly value reported by United Arab Emirates.",
        json_schema_extra={"x-widget_config": {"headerName": "United Arab Emirates"}},
    )
    united_kingdom: float | None = Field(
        default=None,
        description="Monthly value reported by United Kingdom.",
        json_schema_extra={"x-widget_config": {"headerName": "United Kingdom"}},
    )
    united_states: float | None = Field(
        default=None,
        description="Monthly value reported by United States.",
        json_schema_extra={"x-widget_config": {"headerName": "United States"}},
    )
    uruguay: float | None = Field(
        default=None,
        description="Monthly value reported by Uruguay.",
        json_schema_extra={"x-widget_config": {"headerName": "Uruguay"}},
    )
    venezuela: float | None = Field(
        default=None,
        description="Monthly value reported by Venezuela.",
        json_schema_extra={"x-widget_config": {"headerName": "Venezuela"}},
    )
    vietnam: float | None = Field(
        default=None,
        description="Monthly value reported by Vietnam.",
        json_schema_extra={"x-widget_config": {"headerName": "Vietnam"}},
    )
    yemen: float | None = Field(
        default=None,
        description="Monthly value reported by Yemen.",
        json_schema_extra={"x-widget_config": {"headerName": "Yemen"}},
    )
