### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_compare(Container):
    """/equity/compare
    company_facts
    groups
    peers
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def company_facts(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): sec."
            ),
        ] = None,
        fact: Annotated[
            str,
            OpenBBField(
                description="The fact to lookup, typically a GAAP-reporting measure. Choices vary by provider."
            ),
        ] = "",
        provider: Annotated[
            Optional[Literal["sec"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: sec."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Copmare reported company facts and fundamental data points.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): sec.
        fact : str
            The fact to lookup, typically a GAAP-reporting measure. Choices vary by provider.
        provider : Optional[Literal['sec']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: sec.
        year : Optional[int]
            The year to retrieve the data for. If not provided, the current year is used. When symbol(s) are provided, excluding the year will return all reported values for the concept. (provider: sec)
        fiscal_period : Optional[Literal['fy', 'q1', 'q2', 'q3', 'q4']]
            The fiscal period to retrieve the data for. If not provided, the most recent quarter is used. This parameter is ignored when a symbol is supplied. (provider: sec)
        instantaneous : bool
            Whether to retrieve instantaneous data. See the notes above for more information. Defaults to False. Some facts are only available as instantaneous data.
        The function will automatically attempt the inverse of this parameter if the initial fiscal quarter request fails. This parameter is ignored when a symbol is supplied. (provider: sec)
        use_cache : bool
            Whether to use cache for the request. Defaults to True. (provider: sec)

        Returns
        -------
        OBBject
            results : List[CompareCompanyFacts]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompareCompanyFacts
        -------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        value : float
            The reported value of the fact or concept.
        reported_date : Optional[date]
            The date when the report was filed.
        period_beginning : Optional[date]
            The start date of the reporting period.
        period_ending : Optional[date]
            The end date of the reporting period.
        fiscal_year : Optional[int]
            The fiscal year.
        fiscal_period : Optional[str]
            The fiscal period of the fiscal year.
        cik : Optional[Union[str, int]]
            Central Index Key (CIK) for the requested entity. (provider: sec)
        location : Optional[str]
            Geographic location of the reporting entity. (provider: sec)
        form : Optional[str]
            The SEC form associated with the fact or concept. (provider: sec)
        frame : Optional[str]
            The frame ID associated with the fact or concept, if applicable. (provider: sec)
        accession : Optional[str]
            SEC filing accession number associated with the reported fact or concept. (provider: sec)
        fact : Optional[str]
            The display name of the fact or concept. (provider: sec)
        unit : Optional[str]
            The unit of measurement for the fact or concept. (provider: sec)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.compare.company_facts(provider='sec')
        >>> obb.equity.compare.company_facts(provider='sec', fact='PaymentsForRepurchaseOfCommonStock', year=2023)
        >>> obb.equity.compare.company_facts(provider='sec', symbol='NVDA,AAPL,AMZN,MSFT,GOOG,SMCI', fact='RevenueFromContractWithCustomerExcludingAssessedTax', year=2024)
        """  # noqa: E501

        return self._run(
            "/equity/compare/company_facts",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.compare.company_facts",
                        ("sec",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "fact": fact,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "sec": {"multiple_items_allowed": True, "choices": None}
                    },
                    "fact": {
                        "sec": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "AccountsPayableCurrent",
                                "AccountsReceivableNet",
                                "AccountsReceivableNetCurrent",
                                "AccrualForTaxesOtherThanIncomeTaxesCurrent",
                                "AccrualForTaxesOtherThanIncomeTaxesCurrentAndNoncurrent",
                                "AccruedIncomeTaxesCurrent",
                                "AccruedIncomeTaxesNoncurrent",
                                "AccruedInsuranceCurrent",
                                "AccruedLiabilitiesCurrent",
                                "AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
                                "AccumulatedOtherComprehensiveIncomeLossNetOfTax",
                                "AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets",
                                "AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue",
                                "AdvertisingExpense",
                                "AllocatedShareBasedCompensationExpense",
                                "AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount",
                                "AssetImpairmentCharges",
                                "Assets",
                                "AssetsCurrent",
                                "AssetsNoncurrent",
                                "BuildingsAndImprovementsGross",
                                "CapitalLeaseObligationsCurrent",
                                "CapitalLeaseObligationsNoncurrent",
                                "Cash",
                                "CashAndCashEquivalentsAtCarryingValue",
                                "CashCashEquivalentsAndShortTermInvestments",
                                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
                                "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                                "CommercialPaper",
                                "CommitmentsAndContingencies",
                                "CommonStockDividendsPerShareCashPaid",
                                "CommonStockDividendsPerShareDeclared",
                                "CommonStocksIncludingAdditionalPaidInCapital",
                                "ComprehensiveIncomeNetOfTax",
                                "ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest",
                                "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest",
                                "ConstructionInProgressGross",
                                "ContractWithCustomerAssetNet",
                                "ContractWithCustomerLiability",
                                "ContractWithCustomerLiabilityCurrent",
                                "ContractWithCustomerLiabilityNoncurrent",
                                "CostOfGoodsAndServicesSold",
                                "CostOfRevenue",
                                "CurrentFederalTaxExpenseBenefit",
                                "CurrentForeignTaxExpenseBenefit",
                                "CurrentIncomeTaxExpenseBenefit",
                                "CurrentStateAndLocalTaxExpenseBenefit",
                                "DebtInstrumentFaceAmount",
                                "DebtInstrumentFairValue",
                                "DebtLongtermAndShorttermCombinedAmount",
                                "DeferredFederalIncomeTaxExpenseBenefit",
                                "DeferredForeignIncomeTaxExpenseBenefit",
                                "DeferredIncomeTaxExpenseBenefit",
                                "DeferredIncomeTaxLiabilities",
                                "DeferredIncomeTaxLiabilitiesNet",
                                "DeferredIncomeTaxesAndTaxCredits",
                                "DeferredRevenue",
                                "DeferredTaxAssetsGross",
                                "DeferredTaxAssetsLiabilitiesNet",
                                "DeferredTaxAssetsNet",
                                "DeferredTaxLiabilities",
                                "DefinedContributionPlanCostRecognized",
                                "Depreciation",
                                "DepreciationAmortizationAndAccretionNet",
                                "DepreciationAmortizationAndOther",
                                "DepreciationAndAmortization",
                                "DepreciationDepletionAndAmortization",
                                "DerivativeCollateralObligationToReturnCash",
                                "DerivativeCollateralRightToReclaimCash",
                                "DerivativeFairValueOfDerivativeNet",
                                "DerivativeLiabilityCollateralRightToReclaimCashOffset",
                                "DerivativeNotionalAmount",
                                "DistributedEarnings",
                                "Dividends",
                                "DividendsCash",
                                "DividendsPayableAmountPerShare",
                                "DividendsPayableCurrent",
                                "EarningsPerShareBasic",
                                "EarningsPerShareDiluted",
                                "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                                "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations",
                                "EmployeeRelatedLiabilitiesCurrent",
                                "EmployeeRelatedLiabilitiesCurrentAndNoncurrent",
                                "EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense",
                                "FinanceLeaseInterestExpense",
                                "FinanceLeaseInterestPaymentOnLiability",
                                "FinanceLeaseLiability",
                                "FinanceLeaseLiabilityCurrent",
                                "FinanceLeaseLiabilityNoncurrent",
                                "FinanceLeaseLiabilityPaymentsDue",
                                "FinanceLeaseLiabilityPaymentsDueAfterYearFive",
                                "FinanceLeaseLiabilityPaymentsDueNextTwelveMonths",
                                "FinanceLeaseLiabilityPaymentsDueYearFive",
                                "FinanceLeaseLiabilityPaymentsDueYearFour",
                                "FinanceLeaseLiabilityPaymentsDueYearThree",
                                "FinanceLeaseLiabilityPaymentsDueYearTwo",
                                "FinanceLeaseLiabilityPaymentsRemainderOfFiscalYear",
                                "FinanceLeaseLiabilityUndiscountedExcessAmount",
                                "FinanceLeasePrincipalPayments",
                                "FinanceLeaseRightOfUseAsset",
                                "FinancingReceivableAllowanceForCreditLosses",
                                "FiniteLivedIntangibleAssetsNet",
                                "FixturesAndEquipmentGross",
                                "GainLossOnInvestments",
                                "GainLossOnInvestmentsAndDerivativeInstruments",
                                "GainLossOnSaleOfBusiness",
                                "GainsLossesOnExtinguishmentOfDebt",
                                "GeneralAndAdministrativeExpense",
                                "Goodwill",
                                "GrossProfit",
                                "ImpairmentOfIntangibleAssetsExcludingGoodwill",
                                "ImpairmentOfIntangibleAssetsIndefinitelivedExcludingGoodwill",
                                "IncomeLossFromContinuingOperations",
                                "IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity",
                                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                                "IncomeLossFromContinuingOperationsPerBasicShare",
                                "IncomeLossFromContinuingOperationsPerDilutedShare",
                                "IncomeTaxExpenseBenefit",
                                "IncomeTaxesPaid",
                                "IncomeTaxesPaidNet",
                                "IncreaseDecreaseInAccountsAndOtherReceivables",
                                "IncreaseDecreaseInAccountsPayable",
                                "IncreaseDecreaseInAccountsReceivable",
                                "IncreaseDecreaseInAccruedIncomeTaxesPayable",
                                "IncreaseDecreaseInAccruedLiabilities",
                                "IncreaseDecreaseInAccruedTaxesPayable",
                                "IncreaseDecreaseInContractWithCustomerLiability",
                                "IncreaseDecreaseInDeferredIncomeTaxes",
                                "IncreaseDecreaseInInventories",
                                "IncreaseDecreaseInOtherCurrentAssets",
                                "IncreaseDecreaseInOtherCurrentLiabilities",
                                "IncreaseDecreaseInOtherNoncurrentAssets",
                                "IncreaseDecreaseInOtherNoncurrentLiabilities",
                                "IncreaseDecreaseInPensionPlanObligations",
                                "IncrementalCommonSharesAttributableToShareBasedPaymentArrangements",
                                "InterestAndDebtExpense",
                                "InterestExpenseDebt",
                                "InterestIncomeExpenseNet",
                                "InterestPaid",
                                "InterestPaidNet",
                                "InventoryNet",
                                "InvestmentIncomeInterest",
                                "Land",
                                "LeaseAndRentalExpense",
                                "LesseeOperatingLeaseLiabilityPaymentsDue",
                                "LesseeOperatingLeaseLiabilityPaymentsDueAfterYearFive",
                                "LesseeOperatingLeaseLiabilityPaymentsDueNextTwelveMonths",
                                "LesseeOperatingLeaseLiabilityPaymentsDueYearFive",
                                "LesseeOperatingLeaseLiabilityPaymentsDueYearFour",
                                "LesseeOperatingLeaseLiabilityPaymentsDueYearThree",
                                "LesseeOperatingLeaseLiabilityPaymentsDueYearTwo",
                                "LesseeOperatingLeaseLiabilityPaymentsRemainderOfFiscalYear",
                                "LettersOfCreditOutstandingAmount",
                                "Liabilities",
                                "LiabilitiesAndStockholdersEquity",
                                "LiabilitiesCurrent",
                                "LineOfCredit",
                                "LineOfCreditFacilityMaximumBorrowingCapacity",
                                "LongTermDebt",
                                "LongTermDebtCurrent",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo",
                                "LongTermDebtMaturitiesRepaymentsOfPrincipalRemainderOfFiscalYear",
                                "LongTermDebtNoncurrent",
                                "LongTermInvestments",
                                "LossContingencyEstimateOfPossibleLoss",
                                "MachineryAndEquipmentGross",
                                "MarketableSecuritiesCurrent",
                                "MarketableSecuritiesNoncurrent",
                                "MinorityInterest",
                                "NetCashProvidedByUsedInFinancingActivities",
                                "NetCashProvidedByUsedInInvestingActivities",
                                "NetCashProvidedByUsedInOperatingActivities",
                                "NetIncomeLoss",
                                "NetIncomeLossAttributableToNoncontrollingInterest",
                                "NetIncomeLossAttributableToNonredeemableNoncontrollingInterest",
                                "NetIncomeLossAttributableToRedeemableNoncontrollingInterest",
                                "NoncurrentAssets",
                                "NoncurrentAssets",
                                "NoninterestIncome",
                                "NonoperatingIncomeExpense",
                                "NotesReceivableNet",
                                "OperatingExpenses",
                                "OperatingIncomeLoss",
                                "OperatingLeaseCost",
                                "OperatingLeaseLiability",
                                "OperatingLeaseLiabilityCurrent",
                                "OperatingLeaseLiabilityNoncurrent",
                                "OperatingLeaseRightOfUseAsset",
                                "OtherAccruedLiabilitiesCurrent",
                                "OtherAssetsCurrent",
                                "OtherAssetsNoncurrent",
                                "OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax",
                                "OtherComprehensiveIncomeLossCashFlowHedgeGainLossAfterReclassificationAndTax",
                                "OtherComprehensiveIncomeLossDerivativeInstrumentGainLossafterReclassificationandTax",
                                "OtherComprehensiveIncomeLossDerivativeInstrumentGainLossbeforeReclassificationafterTax",
                                "OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax",
                                "OtherComprehensiveIncomeLossNetOfTax",
                                "OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent",
                                "OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuringPeriodNetOfTax",
                                "OtherIncome",
                                "OtherLiabilitiesCurrent",
                                "OtherLiabilitiesNoncurrent",
                                "OtherLongTermDebt",
                                "OtherNoncashIncomeExpense",
                                "PaymentsForCapitalImprovements",
                                "PaymentsForProceedsFromBusinessesAndInterestInAffiliates",
                                "PaymentsForProceedsFromOtherInvestingActivities",
                                "PaymentsForRent",
                                "PaymentsForRepurchaseOfCommonStock",
                                "PaymentsOfDebtExtinguishmentCosts",
                                "PaymentsOfDividends",
                                "PaymentsOfDividendsMinorityInterest",
                                "PaymentsToAcquireInvestments",
                                "PaymentsToAcquirePropertyPlantAndEquipment",
                                "PreferredStockSharesOutstanding",
                                "PreferredStockValue",
                                "PrepaidExpenseAndOtherAssetsCurrent",
                                "PrepaidExpenseCurrent",
                                "ProceedsFromDebtMaturingInMoreThanThreeMonths",
                                "ProceedsFromDebtNetOfIssuanceCosts",
                                "ProceedsFromDivestitureOfBusinesses",
                                "ProceedsFromInvestments",
                                "ProceedsFromIssuanceOfCommonStock",
                                "ProceedsFromIssuanceOfDebt",
                                "ProceedsFromIssuanceOfLongTermDebt",
                                "ProceedsFromIssuanceOfUnsecuredDebt",
                                "ProceedsFromIssuanceOrSaleOfEquity",
                                "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities",
                                "ProceedsFromPaymentsForOtherFinancingActivities",
                                "ProceedsFromPaymentsToMinorityShareholders",
                                "ProceedsFromRepaymentsOfShortTermDebt",
                                "ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess",
                                "ProceedsFromSaleOfPropertyPlantAndEquipment",
                                "ProceedsFromStockOptionsExercised",
                                "ProfitLoss",
                                "PropertyPlantAndEquipmentGross",
                                "PropertyPlantAndEquipmentNet",
                                "ReceivablesNetCurrent",
                                "RedeemableNoncontrollingInterestEquityCarryingAmount",
                                "RepaymentsOfDebtMaturingInMoreThanThreeMonths",
                                "RepaymentsOfLongTermDebt",
                                "ResearchAndDevelopmentExpense",
                                "RestrictedCash",
                                "RestrictedCashAndCashEquivalents",
                                "RestrictedStockExpense",
                                "RestructuringCharges",
                                "RetainedEarningsAccumulatedDeficit",
                                "RevenueFromContractWithCustomerExcludingAssessedTax",
                                "Revenues",
                                "SecuredLongTermDebt",
                                "SellingAndMarketingExpense",
                                "SellingGeneralAndAdministrativeExpense",
                                "ShareBasedCompensation",
                                "ShortTermBorrowings",
                                "ShortTermInvestments",
                                "StockIssuedDuringPeriodValueNewIssues",
                                "StockOptionPlanExpense",
                                "StockRedeemedOrCalledDuringPeriodValue",
                                "StockRepurchasedAndRetiredDuringPeriodValue",
                                "StockRepurchasedDuringPeriodValue",
                                "StockholdersEquity",
                                "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                                "StockholdersEquityOther",
                                "TaxesPayableCurrent",
                                "TradingSecuritiesDebt",
                                "TreasuryStockAcquiredAverageCostPerShare",
                                "TreasuryStockSharesAcquired",
                                "UnrealizedGainLossOnInvestments",
                                "UnrecognizedTaxBenefits",
                                "UnsecuredDebt",
                                "VariableLeaseCost",
                                "WeightedAverageNumberDilutedSharesOutstandingAdjustment",
                                "WeightedAverageNumberOfDilutedSharesOutstanding",
                                "WeightedAverageNumberOfSharesOutstandingBasic",
                            ],
                        }
                    },
                    "fiscal_period": {
                        "sec": {
                            "multiple_items_allowed": False,
                            "choices": ["fy", "q1", "q2", "q3", "q4"],
                        }
                    },
                },
            )
        )

    @exception_handler
    @validate
    def groups(
        self,
        group: Annotated[
            Optional[str],
            OpenBBField(
                description="The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider."
            ),
        ] = None,
        metric: Annotated[
            Optional[str],
            OpenBBField(
                description="The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["finviz"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get company data grouped by sector, industry or country and display either performance or valuation metrics.

        Valuation metrics include price to earnings, price to book, price to sales ratios and price to cash flow.
        Performance metrics include the stock price change for different time periods.


        Parameters
        ----------
        group : Optional[str]
            The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider.
        metric : Optional[str]
            The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider.
        provider : Optional[Literal['finviz']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: finviz.

        Returns
        -------
        OBBject
            results : List[CompareGroups]
                Serializable results.
            provider : Optional[Literal['finviz']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompareGroups
        -------------
        name : str
            Name or label of the group.
        stocks : Optional[int]
            The number of stocks in the group. (provider: finviz)
        market_cap : Optional[int]
            The market cap of the group. (provider: finviz)
        performance_1d : Optional[float]
            The performance in the last day, as a normalized percent. (provider: finviz)
        performance_1w : Optional[float]
            The performance in the last week, as a normalized percent. (provider: finviz)
        performance_1m : Optional[float]
            The performance in the last month, as a normalized percent. (provider: finviz)
        performance_3m : Optional[float]
            The performance in the last quarter, as a normalized percent. (provider: finviz)
        performance_6m : Optional[float]
            The performance in the last half year, as a normalized percent. (provider: finviz)
        performance_1y : Optional[float]
            The performance in the last year, as a normalized percent. (provider: finviz)
        performance_ytd : Optional[float]
            The performance in the year to date, as a normalized percent. (provider: finviz)
        dividend_yield : Optional[float]
            The dividend yield of the group, as a normalized percent. (provider: finviz)
        pe : Optional[float]
            The P/E ratio of the group. (provider: finviz)
        forward_pe : Optional[float]
            The forward P/E ratio of the group. (provider: finviz)
        peg : Optional[float]
            The PEG ratio of the group. (provider: finviz)
        eps_growth_past_5y : Optional[float]
            The EPS growth of the group for the past 5 years, as a normalized percent. (provider: finviz)
        eps_growth_next_5y : Optional[float]
            The estimated EPS growth of the groupo for the next 5 years, as a normalized percent. (provider: finviz)
        sales_growth_past_5y : Optional[float]
            The sales growth of the group for the past 5 years, as a normalized percent. (provider: finviz)
        float_short : Optional[float]
            The percent of the float shorted for the group, as a normalized value. (provider: finviz)
        analyst_recommendation : Optional[float]
            The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell. (provider: finviz)
        volume : Optional[int]
            The trading volume. (provider: finviz)
        volume_average : Optional[int]
            The 3-month average volume of the group. (provider: finviz)
        volume_relative : Optional[float]
            The relative volume compared to the 3-month average volume. (provider: finviz)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.compare.groups(provider='finviz')
        >>> # Group by sector and analyze valuation.
        >>> obb.equity.compare.groups(group='sector', metric='valuation', provider='finviz')
        >>> # Group by industry and analyze performance.
        >>> obb.equity.compare.groups(group='industry', metric='performance', provider='finviz')
        >>> # Group by country and analyze valuation.
        >>> obb.equity.compare.groups(group='country', metric='valuation', provider='finviz')
        """  # noqa: E501

        return self._run(
            "/equity/compare/groups",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.compare.groups",
                        ("finviz",),
                    )
                },
                standard_params={
                    "group": group,
                    "metric": metric,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def peers(
        self,
        symbol: Annotated[str, OpenBBField(description="Symbol to get data for.")],
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get the closest peers for a given company.

        Peers consist of companies trading on the same exchange, operating within the same sector
        and with comparable market capitalizations.


        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.

        Returns
        -------
        OBBject
            results : EquityPeers
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityPeers
        -----------
        peers_list : List[str]
            A list of equity peers based on sector, exchange and market cap.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.compare.peers(symbol='AAPL', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/compare/peers",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "equity.compare.peers",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )
