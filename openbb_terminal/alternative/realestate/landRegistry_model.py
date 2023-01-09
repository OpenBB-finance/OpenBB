"""  UK Land Registry Model """
__docformat__ = "numpy"

import logging
import io
import pandas as pd
from SPARQLWrapper.Wrapper import CSV, SPARQLWrapper

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


def pcd_format(postcode: str):
    return (
        postcode[0 : len(postcode) - 3].strip()
        + " "
        + postcode[len(postcode) - 3 : len(postcode)]
    )


@log_start_end(log=logger)
def get_estate_sales(postcode: str) -> pd.DataFrame:

    """All sales for specified postcode.

    Parameters
    ----------
    postcode : str
        Postcode


    Returns
    -------
    pd.DataFrame
        All sales with that postcode
    """

    if not postcode:
        return pd.DataFrame()

    # the upper is done since SDK calls don't appear to go through the controller
    pcd_postcode = pcd_format(postcode.upper())

    query = f"""
                PREFIX  lrppi: <http://landregistry.data.gov.uk/def/ppi/>
                PREFIX  rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX  owl:  <http://www.w3.org/2002/07/owl#>
                PREFIX  lrcommon: <http://landregistry.data.gov.uk/def/common/>
                PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
                PREFIX  ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
                PREFIX  skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX  sr:   <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>

                SELECT  ?paon ?saon ?street ?town ?county ?postcode ?amount ?date ?id ?category
                WHERE
                    {{ VALUES ?postcode {{ "{pcd_postcode}" }}
                    ?addr   lrcommon:postcode     ?postcode .
                    ?transx lrppi:propertyAddress  ?addr ;
                            lrppi:pricePaid       ?amount ;
                            lrppi:transactionId ?id ;
                            lrppi:transactionDate  ?date .
                    ?transx lrppi:transactionCategory/skos:prefLabel ?category.

                    OPTIONAL {{ ?addr  lrcommon:county  ?county }}
                    OPTIONAL {{ ?addr  lrcommon:paon  ?paon }}
                    OPTIONAL {{ ?addr  lrcommon:saon  ?saon }}
                    OPTIONAL {{ ?addr  lrcommon:street  ?street }}
                    OPTIONAL {{ ?addr  lrcommon:town  ?town }}
                    }}
                ORDER BY DESC(?date)
            """
    endpoint = "http://landregistry.data.gov.uk/landregistry/query"

    #  df = sparql_dataframe.get(endpoint, query)

    df = pd.DataFrame()
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(CSV)
    sparql.setQuery(query)

    results = sparql.query().convert()
    if isinstance(results, bytes):
        _csv = io.StringIO(results.decode("utf-8"))
        # print( pd.read_csv(_csv, sep=","))
        df = pd.read_csv(_csv, sep=",")

    return df


@log_start_end(log=logger)
def get_towns_sold_prices(
    town: str, startdate: str = "2010-01-01", enddate: str = ""
) -> pd.DataFrame:
    """Get towns sold house price data.

    Parameters
    ----------
    town : str
        town

    startdate : str
        startDate

    enddate : str
        endDate


    Returns
    -------
    pd.DataFrame
        All sales for that town within the date range specified
    """

    # the upper is done since SDK calls don't appear to go through the controller
    town = town.upper()

    query = f"""
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                prefix owl: <http://www.w3.org/2002/07/owl#>
                prefix xsd: <http://www.w3.org/2001/XMLSchema#>
                prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
                prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
                prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
                prefix skos: <http://www.w3.org/2004/02/skos/core#>
                prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>

                SELECT ?paon ?saon ?street   ?county ?postcode ?amount ?date ?category 
                WHERE
                {{
                VALUES ?town {{"{town}"^^xsd:string}}
                
                ?addr lrcommon:town ?town ;
                        lrcommon:postcode ?postcode.

                ?transx lrppi:propertyAddress ?addr ;
                        lrppi:pricePaid ?amount ;
                        lrppi:transactionDate ?date ;
                        lrppi:transactionCategory/skos:prefLabel ?category.
                
                FILTER (
                    ?date > "{startdate}"^^xsd:date &&
                    ?date < "{enddate}"^^xsd:date
                ).

                OPTIONAL {{?addr lrcommon:county ?county}}
                OPTIONAL {{?addr lrcommon:paon ?paon}}
                OPTIONAL {{?addr lrcommon:saon ?saon}}
                OPTIONAL {{?addr lrcommon:saon ?postcode}}
                OPTIONAL {{?addr lrcommon:street ?street}}
                }}
                ORDER BY (?date && ?postcode)
            """

    endpoint = "http://landregistry.data.gov.uk/landregistry/query"

    df = pd.DataFrame()
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(CSV)
    sparql.setQuery(query)
    sparql.method = "POST"

    results = sparql.query().convert()
    if isinstance(results, bytes):
        _csv = io.StringIO(results.decode("utf-8"))
        df = pd.read_csv(_csv, sep=",")

    return df


@log_start_end(log=logger)
def get_region_stats(
    region: str, startdate: str = "2010-01-01", enddate: str = ""
) -> pd.DataFrame:
    """Get regional house price statistics.

    Parameters
    ----------
    region : str
        region

    startdate : str
        startDate

    enddate : str
        endDate


    Returns
    -------
    pd.DataFrame
        All stats for that region within the date range specified
    """

    region = region.lower()

    query = f"""
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                prefix owl: <http://www.w3.org/2002/07/owl#>
                prefix xsd: <http://www.w3.org/2001/XMLSchema#>
                prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
                prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
                prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
                prefix skos: <http://www.w3.org/2004/02/skos/core#>
                prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>

                SELECT  ?month ?avgPrice ?avgPriceCash ?totalSalesVolume ?avgPriceExistingProperty ?avgPriceFirstTimeBuyer 
                ?avgPriceDetached ?hpi  ?detachedhpi ?newbuildhpi 
                {{
                    values ?refRegion {{<http://landregistry.data.gov.uk/id/region/{region}>}}
                    ?region ukhpi:refPeriodStart ?month ;
                            ukhpi:housePriceIndex ?hpi ; 
                            ukhpi:refRegion ?refRegion ;
                            ukhpi:averagePrice ?avgPrice ;
                            ukhpi:averagePriceCash ?avgPriceCash ;
                            ukhpi:salesVolume ?totalSalesVolume ;
                            ukhpi:averagePriceDetached ?avgPriceDetached ;
                            ukhpi:averagePriceExistingProperty ?avgPriceExistingProperty ;
                            ukhpi:averagePriceFirstTimeBuyer ?avgPriceFirstTimeBuyer ;
                            ukhpi:housePriceIndexDetached ?detachedhpi ;
                            ukhpi:housePriceIndexNewBuild ?newbuildhpi .
                    ?refRegion rdfs:label ?regionLabel .
                    FILTER(LANG(?regionLabel) = "en").
                    FILTER (
                        ?month > "{startdate}"^^xsd:date &&
                        ?month < "{enddate}"^^xsd:date
                    )
                    
                    OPTIONAL {{?region ukhpi:housePriceIndexDetached ?detachedhpi}}
                    OPTIONAL {{?region ukhpi:housePriceIndexNewBuild ?newbuildhpi }}
                    OPTIONAL {{?region ukhpi:averagePrice ?averagePrice }}
                }}
                ORDER BY (?month)
            """

    endpoint = "http://landregistry.data.gov.uk/landregistry/query"

    df = pd.DataFrame()
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(CSV)
    sparql.setQuery(query)
    sparql.method = "POST"

    results = sparql.query().convert()
    if isinstance(results, bytes):
        _csv = io.StringIO(results.decode("utf-8"))
        df = pd.read_csv(_csv, sep=",")

    return df
