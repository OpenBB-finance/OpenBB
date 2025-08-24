### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Any, Literal, Optional

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_uscongress(Container):
    """/uscongress
    bill_info
    bill_text
    bill_text_urls
    bills
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def bill_info(
        self,
        provider: Annotated[
            Optional[Literal["congress_gov"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get summary, status, and other metadata for a specific bill.

        Enter the URL of the bill as: https://api.congress.gov/v3/bill/119/hr/131?

        URLs for bills can be found from the `uscongress.bills` endpoint.

        The raw JSON response from the API will be returned along with a formatted
        text version of the key information from the raw response.

        In OpenBB Workspace, this command returns as a Markdown widget.


        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov.
        bill_url : Optional[str]
            Enter a base URL of a bill (e.g., 'https://api.congress.gov/v3/bill/119/s/1947?format=json'). Alternatively, you can enter a bill number (e.g., '119/s/1947'). (provider: congress_gov)

        Returns
        -------
        OBBject
            results : CongressBillInfo
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CongressBillInfo
        ----------------
        markdown_content : Optional[str]
            Aggregated metadata for the bill in Markdown format. (provider: congress_gov)
        raw_data : Optional[dict[str, Any]]
            Raw JSON data from the collected bill information. (provider: congress_gov)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.uscongress.bill_info(provider='congress_gov', bill_url='https://api.congress.gov/v3/bill/119/s/1947?')
        >>> # The bill URL can be shortened to just the bill number (e.g., '119/s/1947').
        >>> obb.uscongress.bill_info(bill_url='119/s/1947', provider='congress_gov')
        """  # noqa: E501

        return self._run(
            "/uscongress/bill_info",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "uscongress.bill_info",
                        ("congress_gov",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "bill_url": {
                        "congress_gov": {
                            "x-widget_config": {
                                "label": "Bill URL",
                                "description": "Enter a base URL of a bill (e.g., 'https://api.congress.gov/v3/bill/119/s/1947?'). Alternatively, you can enter a bill number (e.g., '119/s/1947'). Create a group on the 'Bill URL' field of the 'Congressional Bills' widget and click on the cell to view summary and metadata.",
                                "value": "119/hr/1",
                            }
                        }
                    }
                },
            ),
        )

    @exception_handler
    @validate
    def bill_text(
        self,
        provider: Annotated[
            Optional[Literal["congress_gov"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Download the text of a specific bill in PDF format.

        This endpoint accepts a list of URLs to download and returns the base64-encoded
        PDF content along with the filename.

        In OpenBB Workspace, this command returns as a multi-file viewer widget.

        This command outputs only the results array of the OBBject.


        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov.
        urls : Union[str, list[str], dict[str, list[str]], None]
            list of direct bill URLs to download. Multiple comma separated items allowed. (provider: congress_gov)

        Returns
        -------
        OBBject
            results : list[CongressBillText]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CongressBillText
        ----------------
        error_type : Optional[str]
            Error type if any error occurs during the download. (provider: congress_gov)
        content : Optional[str]
            Base64-encoded PDF document. (provider: congress_gov)
        filename : Optional[str]
            The filename of the downloaded PDF. (provider: congress_gov)
        data_format : Optional[dict[str, str]]
            Data format information, including data type and filename. (provider: congress_gov)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.uscongress.bill_text(provider='congress_gov', urls='['https://www.congress.gov/119/bills/hr1/BILLS-119hr1eh.pdf']')
        """  # noqa: E501

        return self._run(
            "/uscongress/bill_text",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "uscongress.bill_text",
                        ("congress_gov",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "urls": {
                        "congress_gov": {
                            "multiple_items_allowed": True,
                            "choices": None,
                        }
                    }
                },
                data_processing=True,
            ),
        )

    @exception_handler
    @validate
    def bill_text_urls(
        self,
        bill_url: Annotated[str, OpenBBField(description="")],
        is_workspace: Annotated[bool, OpenBBField(description="")] = False,
        provider: Annotated[
            Optional[str], OpenBBField(description="")
        ] = "congress_gov",
        **kwargs: Any
    ) -> list:
        """Helper function to populate document choices for a specific bill.

        This function is used by the Congressional Bills Viewer widget, in OpenBB Workspace,
        to populate PDF document choices for the selected bill.

        When 'is_workspace' is False (default), it returns a list of the available text versions
        of the specified bill and their download links for the different formats.

        Parameters
        ----------
        bill_url : str
            The base URL of the bill (e.g., "https://api.congress.gov/v3/bill/119/s/1947?format=json").
            This can also be a shortened version like "119/s/1947".
        provider : str
            The provider name, always "congress_gov". This is a dummy parameter.
        is_workspace : bool
            Whether the request is coming from the OpenBB Workspace.
            This alters the output format to conform to the Workspace's expectations.

        Returns
        -------
        list[dict]
            Returns a list of dictionaries with 'label' and 'value' keys, when `is_workspace` is True.
            Otherwise, returns the 'text' object from the Congress.gov API response.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.uscongress.bill_text_urls(provider='congress_gov', bill_url='https://api.congress.gov/v3/bill/119/s/1947?')
        >>> obb.uscongress.bill_text_urls(provider='congress_gov', bill_url='119/s/1947')
        """  # noqa: E501

        return self._run(
            "/uscongress/bill_text_urls",
            **filter_inputs(
                bill_url=bill_url,
                provider=provider,
                is_workspace=is_workspace,
                **kwargs,
            ),
        )

    @exception_handler
    @validate
    def bills(
        self,
        provider: Annotated[
            Optional[Literal["congress_gov"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get and filter lists of Congressional Bills.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: congress_gov.
        congress : Optional[int]
            Congress number (e.g., 118 for the 118th Congress). The 103rd Congress started in 1993, which is the earliest date supporting full text versions. Each Congress spans two years, starting in odd-numbered years. (provider: congress_gov)
        bill_type : Optional[str]
            Bill type (e.g., "hr" for House bills).

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

             (provider: congress_gov)
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format. Filters bills by the last updated date. (provider: congress_gov)
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format. Filters bills by the last updated date. (provider: congress_gov)
        limit : Optional[int]
            The number of data entries to return. When None, default sets to 100 (max 250). Set to 0 for no limit (must be used with 'bill_type' and 'congress'). (provider: congress_gov)
        offset : Optional[int]
            The starting record returned. 0 is the first record. (provider: congress_gov)
        sort_by : Literal['asc', 'desc']
            Sort by update date. Default is latest first. (provider: congress_gov)

        Returns
        -------
        OBBject
            results : list[CongressBills]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CongressBills
        -------------
        update_date : Optional[date]
            The date the bill was last updated. (provider: congress_gov)
        latest_action_date : Optional[date]
            The date of the latest action on the bill. (provider: congress_gov)
        bill_url : Optional[str]
            Base URL to the bill for the congress.gov API. (provider: congress_gov)
        congress : Optional[int]
            The congress session number. (provider: congress_gov)
        bill_number : Optional[int]
            The bill number. (provider: congress_gov)
        origin_chamber : Optional[str]
            The chamber where the bill originated. (provider: congress_gov)
        origin_chamber_code : Optional[str]
            The chamber code where the bill originated. (provider: congress_gov)
        bill_type : Optional[str]
            The type of bill (e.g., HR, S). (provider: congress_gov)
        title : Optional[str]
            The title of the bill. (provider: congress_gov)
        latest_action : Optional[str]
            Latest action information for the bill. (provider: congress_gov)
        update_date_including_text : Optional[datetime]
            The date and time the bill text was last updated. (provider: congress_gov)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.uscongress.bills(provider='congress_gov')
        >>> obb.uscongress.bills(start_date='2025-01-01', end_date='2025-01-31', provider='congress_gov')
        >>> # Get all bills of type 's' (Senate) for the 118th Congress.
        >>> obb.uscongress.bills(bill_type='s', congress=118, limit=0, provider='congress_gov')
        """  # noqa: E501

        return self._run(
            "/uscongress/bills",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "uscongress.bills",
                        ("congress_gov",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "congress": {
                        "congress_gov": {"x-widget_config": {"type": "number"}}
                    },
                    "bill_type": {
                        "congress_gov": {
                            "x-widget_config": {
                                "options": [
                                    {"label": "House Bill", "value": "hr"},
                                    {"label": "Senate Bill", "value": "s"},
                                    {
                                        "label": "House Joint Resolution",
                                        "value": "hjres",
                                    },
                                    {
                                        "label": "Senate Joint Resolution",
                                        "value": "sjres",
                                    },
                                    {
                                        "label": "House Concurrent Resolution",
                                        "value": "hconres",
                                    },
                                    {
                                        "label": "Senate Concurrent Resolution",
                                        "value": "sconres",
                                    },
                                    {
                                        "label": "House Simple Resolution",
                                        "value": "hres",
                                    },
                                    {
                                        "label": "Senate Simple Resolution",
                                        "value": "sres",
                                    },
                                ],
                                "value": None,
                                "style": {"popupWidth": 300},
                                "paramName": "bill_type",
                                "label": "Bill Type",
                            }
                        }
                    },
                    "offset": {"congress_gov": {"x-widget_config": {"type": "number"}}},
                },
            ),
        )
