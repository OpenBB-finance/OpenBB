from openbb_terminal.core.session.current_system import set_system_variable

# Suppressing sdk logs
set_system_variable("LOGGING_SUPPRESS", True)

# Import the OpenBB SDK
# pylint: disable=wrong-import-position
from openbb_terminal.sdk import openbb  # noqa: E402

INTERVAL_OPTS = [
    "5m",
    "15m",
    "30m",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
]

STOCKS_ROWS = [
    "sector",
    "market_cap",
    "beta",
    "year_high",
    "year_low",
    "floatShares",
    "sharesShort",
    "exDividendDate",
]

STOCKS_VIEWS = {
    "Raw Data": lambda x, y: x,
    "Percent Change": lambda x, y: x.pct_change(),
    "Rolling Average": lambda x, y: x.rolling(y).mean(),
    "Rolling Variance": lambda x, y: x.rolling(y).var(),
    "Rolling Standard Deviation": lambda x, y: x.rolling(y).var() ** 0.5,
    "Rolling Coefficient of Variation": lambda x, y: (x.rolling(y).var() ** 0.5)
    / (x.rolling(y).mean()),
}


STOCKS_CLEAN_ROW = {
    "sector": "Sector",
    "market_cap": "M Cap",
    "beta": "Beta",
    "year_high": "52W High",
    "year_low": "52W Low",
    "floatShares": "Floats",
    "sharesShort": "Shorts",
    "exDividendDate": "Ex-Div",
}

# pylint: disable=E1101
FORECAST_MODEL_OPTS = {
    "expo": openbb.forecast.expo,  # type: ignore
    "theta": openbb.forecast.theta,  # type: ignore
    "linregr": openbb.forecast.linregr,  # type: ignore
    "regr": openbb.forecast.regr,  # type: ignore
    "rnn": openbb.forecast.rnn,  # type: ignore
    "brnn": openbb.forecast.brnn,  # type: ignore
    "nbeats": openbb.forecast.nbeats,  # type: ignore
    "tcn": openbb.forecast.tcn,  # type: ignore
    "trans": openbb.forecast.trans,  # type: ignore
    "tft": openbb.forecast.tft,  # type: ignore
}

FORECAST_FEAT_ENGS = {
    "ema": openbb.forecast.ema,  # type: ignore
    "sto": openbb.forecast.sto,  # type: ignore
    "rsi": openbb.forecast.rsi,  # type: ignore
    "roc": openbb.forecast.roc,  # type: ignore
    "mom": openbb.forecast.mom,  # type: ignore
    "atr": openbb.forecast.atr,  # type: ignore
    "delta": openbb.forecast.delta,  # type: ignore
    "signal": openbb.forecast.signal,  # type: ignore
}
# pylint: enable=E1101


PLOTLY_MODEBAR = """
<script>
    // Create global variables to for use later
    console.log(window.parent.document.getElementsByClassName("modebar-container"));
    const modebar = window.parent.document.getElementsByClassName("modebar-container")[0];
    const modebar_buttons = modebar.getElementsByClassName("modebar-btn");
    console.log(modebar_buttons);
    let globals = {
        barButtons: {}
    };

    for (let i = 0; i < modebar_buttons.length; i++) {
        // We add the buttons to the global variable for later use
        // and set the border to transparent so we can change the
        // color of the buttons when they are pressed
        let button = modebar_buttons[i];
        button.style.border = "transparent";
        globals.barButtons[button.getAttribute("data-title")] = button;
    }
    console.log(globals.barButtons);
    let home_path = `m786 296v-267q0-15-11-26t-25-10h-214v214h-143v-214h-214q-15 0-25 10t-11 26v267q0
    1 0 2t0 2l321 264 321-264q1-1 1-4z m124 39l-34-41q-5-5-12-6h-2q-7 0-12 3l-386 322-386-322q-7-4-13-4-7
    2-12 7l-35 41q-4 5-3 13t6 12l401 334q18 15 42 15t43-15l136-114v109q0 8 5 13t13 5h107q8 0
    13-5t5-13v-227l122-102q5-5 6-12t-4-13z`;
    globals.barButtons["Reset Axes"] = globals.barButtons["Autoscale"];
    globals.barButtons["Autoscale"].getElementsByTagName("path")[0].setAttribute("d", home_path);
    globals.barButtons["Autoscale"].setAttribute("data-title", "Reset Axes");
</script>
"""


PLOTLY_CONFIG = {
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "modeBarButtons": [
        ["toImage"],
        [
            "drawline",
            "drawopenpath",
            "drawcircle",
            "drawrect",
            "eraseshape",
        ],
        ["zoomIn2d", "zoomOut2d", "autoScale2d", "zoom2d", "pan2d"],
    ],
}
