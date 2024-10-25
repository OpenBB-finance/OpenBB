"""Streamlit News Page"""

# flake8: noqa: I001

from datetime import datetime, timedelta

from openbb import obb
from numpy import nan

import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="News",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown(
    """
<style>
section[data-testid="stSidebar"] {
    top: 1% !important;
    height: 98.25% !important;
    left: 0.33% !important;
    margin-top: 0 !important;
}
section[data-testid="stSidebar"] img {
    margin-top: -75px !important;
    margin-left: -10px !important;
    width: 95% !important;
}
section[data-testid="stVerticalBlock"] {
    gap: 0rem;
}
body {
    line-height: 1.2;
}
</style>
<figure style='text-align: center;'>
    <img src='https://openbb.co/assets/images/ogimages/Homepage.png' />
    <figcaption style='font-size: 0.8em; color: #888;'>Powered by Open Source</figcaption>
</figure>
""",
    unsafe_allow_html=True,
)


button_pressed = False

SUPPORTED_SOURCES = ["benzinga", "biztoc", "intrinio", "fmp", "tiingo"]

providers = [
    d
    for d in list(obb.user.credentials.__dict__.keys())  # type: ignore
    if obb.user.credentials.__dict__[d] is not None  # type: ignore
]
providers = [d.split("_")[0] for d in providers if d.split("_")[0] in SUPPORTED_SOURCES]
news_sources = [d.upper() if d == "fmp" else d.title() for d in providers]

if "news" not in st.session_state:
    st.session_state.news = None

if "biztoc_sources" not in st.session_state:
    st.session_state.biztoc_sources = []
if "news_container" not in st.session_state:
    st.session_state.news_container = st.empty()
if "selected_limit" not in st.session_state:
    st.session_state.selected_limit = 100
if "selected_provider" not in st.session_state:
    if len(news_sources) == 0:
        st.error(
            f"No news sources available. Please check your credentials for one of: {SUPPORTED_SOURCES}"
        )
        st.stop()
    if len(news_sources) > 0:
        st.session_state.selected_provider = (
            "Biztoc" if "Biztoc" in news_sources else news_sources[0]
        )
if "selected_tags" not in st.session_state:
    st.session_state.selected_tags = ""
if "selected_term" not in st.session_state:
    st.session_state.selected_term = ""
if "news_start_date" not in st.session_state:
    st.session_state.news_start_date = (datetime.now() - timedelta(days=2)).date()
if "news_end_date" not in st.session_state:
    st.session_state.news_end_date = datetime.now().date()
if "selected_biztoc_source" not in st.session_state:
    st.session_state.selected_biztoc_source = ""
if "content_type" not in st.session_state:
    st.session_state.content_type = "news"
if "benzinga_tickers" not in st.session_state:
    st.session_state.benzinga_tickers = ""
if "selected_benzinga_channel" not in st.session_state:
    st.session_state.selected_benzinga_channel = ""
if "fmp_tickers" not in st.session_state:
    st.session_state.fmp_tickers = ""
if "intrinio_tickers" not in st.session_state:
    st.session_state.intrinio_tickers = ""
if "tiingo_tickers" not in st.session_state:
    st.session_state.tiingo_tickers = ""
if "tiingo_source" not in st.session_state:
    st.session_state.tiingo_source = ""


def fetch_openbb():
    kwargs = {
        "provider": st.session_state.selected_provider.lower(),
        "limit": st.session_state.selected_limit,
    }
    if st.session_state.selected_provider == "Benzinga":
        kwargs["start_date"] = st.session_state.news_start_date.strftime("%Y-%m-%d")
        kwargs["end_date"] = st.session_state.news_end_date.strftime("%Y-%m-%d")
        kwargs["topics"] = st.session_state.selected_tags
        kwargs["display"] = "full"
        kwargs["page_size"] = 100
        kwargs["channels"] = (
            st.session_state.selected_benzinga_channel.lower()
            if st.session_state.selected_benzinga_channel
            else None
        )
        kwargs["symbol"] = (
            st.session_state.benzinga_tickers
            if st.session_state.benzinga_tickers
            else None
        )

    if st.session_state.selected_provider == "Biztoc":
        kwargs["term"] = st.session_state.selected_term
        kwargs["tag"] = st.session_state.selected_tags
        kwargs["filter"] = "tag" if kwargs.get("tag") else None
        if kwargs.get("filter") is None:
            kwargs["filter"] = "latest"
        kwargs["source"] = (
            st.session_state.selected_biztoc_source
            if st.session_state.selected_biztoc_source
            else None
        )
        kwargs["filter"] = "source" if kwargs.get("source") else kwargs.get("filter")
        if kwargs.get("filter") == "source":
            kwargs.pop("tag")

    if st.session_state.selected_provider == "FMP":
        kwargs["symbol"] = (
            st.session_state.fmp_tickers if st.session_state.fmp_tickers else None
        )

    if st.session_state.selected_provider == "Intrinio":
        kwargs["symbol"] = (
            st.session_state.intrinio_tickers
            if st.session_state.intrinio_tickers
            else None
        )

    if st.session_state.selected_provider == "Tiingo":
        kwargs["start_date"] = st.session_state.news_start_date.strftime("%Y-%m-%d")
        kwargs["end_date"] = st.session_state.news_end_date.strftime("%Y-%m-%d")
        kwargs["symbol"] = (
            st.session_state.tiingo_tickers if st.session_state.tiingo_tickers else None
        )

    kwargs = {key: value for key, value in kwargs.items() if value is not None}

    data = (
        obb.news.company(**kwargs)  # type: ignore
        if kwargs.get("symbol")
        else obb.news.world(**kwargs)  # type: ignore
    )
    if data.results != []:
        return data.to_df().sort_index(ascending=False).reset_index()


def update_data():
    st.session_state.news = fetch_openbb()


with st.sidebar:
    c1, c2 = st.columns(2)
    with c1:
        old_start_date = st.session_state.news_start_date
        old_provider = st.session_state.selected_provider
        st.session_state.selected_provider = st.selectbox(
            label="Provider",
            options=news_sources,
            index=news_sources.index(st.session_state.selected_provider),
        )
        old_tags = st.session_state.selected_tags
        if st.session_state.selected_provider == "Benzinga":
            st.session_state.news_start_date = st.date_input(
                "Start Date", value=old_start_date
            )
            st.session_state.selected_tags = st.text_input(
                label="Tag", value=st.session_state.selected_tags
            )
        old_biztoc_source = st.session_state.selected_biztoc_source
        if st.session_state.selected_provider == "Biztoc":

            st.session_state.selected_biztoc_source = st.text_input(label="Source")
        old_benzinga_tickers = st.session_state.benzinga_tickers
        if st.session_state.selected_provider == "Benzinga":
            st.session_state.benzinga_tickers = st.text_input(
                label="Tickers", value=old_benzinga_tickers
            )
        old_fmp_tickers = st.session_state.fmp_tickers
        if st.session_state.selected_provider == "FMP":
            st.session_state.fmp_tickers = st.text_input(
                label="Tickers", value=old_fmp_tickers
            )
        old_intrinio_tickers = st.session_state.intrinio_tickers
        if st.session_state.selected_provider == "Intrinio":
            st.session_state.intrinio_tickers = st.text_input(
                label="Tickers", value=old_intrinio_tickers
            )
        old_tiingo_tickers = st.session_state.tiingo_tickers
        if st.session_state.selected_provider == "Tiingo":
            st.session_state.news_start_date = st.date_input(
                "Start Date", value=old_start_date
            )
            old_tiingo_tickers = st.session_state.tiingo_tickers
            st.session_state.tiingo_tickers = st.text_input(
                label="Tickers", value=st.session_state.tiingo_tickers
            )
    with c2:
        old_limit = st.session_state.selected_limit
        old_end_date = st.session_state.news_end_date
        st.session_state.selected_limit = st.number_input(
            "Number of Stories", min_value=1, value=100
        )
        old_channel = st.session_state.selected_benzinga_channel
        if st.session_state.selected_provider == "Benzinga":
            st.session_state.news_end_date = st.date_input(
                "End Date", value=old_end_date
            )
            st.session_state.selected_benzinga_channel = st.text_input(
                label="Feed Channel", value=old_channel
            )
        old_term = st.session_state.selected_term
        if st.session_state.selected_provider == "Biztoc":
            st.session_state.selected_term = st.text_input(
                label="Search Term", value=old_term
            )
        if st.session_state.selected_provider == "Tiingo":
            st.session_state.news_end_date = st.date_input(
                "End Date", value=old_end_date
            )

    if any(
        [
            old_start_date != st.session_state.news_start_date,
            old_end_date != st.session_state.news_end_date,
            old_limit != st.session_state.selected_limit,
            old_provider != st.session_state.selected_provider,
            old_tags != st.session_state.selected_tags,
            old_term != st.session_state.selected_term,
            old_biztoc_source != st.session_state.selected_biztoc_source,
            old_channel != st.session_state.selected_benzinga_channel,
            old_benzinga_tickers != st.session_state.benzinga_tickers,
            old_fmp_tickers != st.session_state.fmp_tickers,
            old_intrinio_tickers != st.session_state.intrinio_tickers,
            old_tiingo_tickers != st.session_state.tiingo_tickers,
        ]
    ):
        update_data()

    if st.button("Fetch Data"):
        update_data()


def main():
    with st.session_state.news_container.container():
        st.markdown(
            " <style> div[class^='block-container'] { padding-top: 1rem; } h1 { margin-bottom: -10px; } </style> "
            "<h1 style='text-align: center;'>Headlines and Stories</h1> ",
            unsafe_allow_html=True,
        )
        if st.session_state.news is not None:
            story = -1
            expanded = False
            for i in st.session_state.news.index:
                story += 1
                expanded = story == 0
                text = (
                    st.session_state.news.loc[i].text
                    if "text" in st.session_state.news.loc[i]
                    else st.session_state.news.loc[i].get("title")
                )
                src = st.session_state.news.loc[i].url
                date = str(st.session_state.news.loc[i].date)
                title = st.session_state.news.loc[i].title
                if text and text is not nan and text != "":
                    with st.expander(label=f"{date}  -  {title}", expanded=expanded):
                        st.markdown(
                            f"""
                        <div style='max-width: 90%; margin: auto; word-wrap: break-word;'>
                            <h2 style='text-align: center;'>{title}</h2>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        if st.session_state.selected_provider == "Benzinga":
                            _tags = (
                                st.session_state.news.loc[i].tags
                                if st.session_state.news.loc[i].get("tags")
                                else ""
                            )
                            _stocks = (
                                st.session_state.news.loc[i].stocks
                                if st.session_state.news.loc[i].get("stocks")
                                else ""
                            )
                            _channels = (
                                st.session_state.news.loc[i].channels
                                if st.session_state.news.loc[i].get("channels")
                                else ""
                            )
                            _images = (
                                st.session_state.news.loc[i].images
                                if st.session_state.news.loc[i].get("images")
                                else []
                            )
                            _url = st.session_state.news.loc[i].url
                            st.markdown(
                                """
                            <style>
                            img {
                                max-width: 98%;
                                height: auto;
                                margin: auto;
                            }
                            </style>
                            """,
                                unsafe_allow_html=True,
                            )
                            if _images and _images is not nan:
                                img = _images[0].get("url")
                                if img is not None:
                                    st.markdown(
                                        f"<div style='text-align: center;'><img src='{img}'></div><br></br>",
                                        unsafe_allow_html=True,
                                    )
                            if text is not None:
                                st.markdown(text, unsafe_allow_html=True)
                            st.divider()
                            st.write(_url)
                            if _tags:
                                st.markdown(
                                    f"##### Tags for this story:  \n {_tags}  \n"
                                )
                            if _stocks and _stocks is not nan:
                                st.markdown(f"##### Stocks mentioned:\n {_stocks}  \n")
                            if _channels:
                                st.markdown(
                                    f"##### Channels for this story:  \n {_channels}  \n"
                                )

                        if st.session_state.selected_provider == "Biztoc":
                            if st.session_state.news.loc[i].get("images") not in [
                                None,
                                nan,
                            ]:
                                img = st.session_state.news.loc[i].images[0].get("s")
                                img = (
                                    st.session_state.news.loc[i].images.get("o")
                                    if img is None
                                    else img
                                )
                                if img is not None:
                                    st.markdown(
                                        f"<div style='text-align: center;'><img src='{img}'></div><br></br>",
                                        unsafe_allow_html=True,
                                    )
                            if text:
                                st.markdown(text, unsafe_allow_html=True)
                            st.write(src)
                            _story_tags = st.session_state.news.loc[i].get("tags")
                            _story_tags = ",".join(_story_tags) if _story_tags else ""
                            if _story_tags:
                                st.divider()
                                st.markdown(
                                    f"##### Tags for this story: \n {_story_tags}  \n\n"
                                )

                        if st.session_state.selected_provider == "Intrinio":
                            _tags = st.session_state.news.loc[i].get("tags")
                            _stocks = (
                                st.session_state.news.loc[i]["company"].get("ticker")
                                if st.session_state.news.loc[i].get("company")
                                else None
                            )
                            _images = st.session_state.news.loc[i].get("images")
                            _url = st.session_state.news.loc[i].get("url")
                            st.markdown(text, unsafe_allow_html=True)
                            if _url:
                                st.write(_url)
                            if _stocks and _stocks is not nan:
                                st.divider()
                                st.markdown(f"##### Stocks mentioned:\n {_stocks}  \n")

                        if st.session_state.selected_provider == "FMP":
                            _url = st.session_state.news.loc[i].get("url")
                            _images = st.session_state.news.loc[i].get("images")
                            _symbols = st.session_state.news.loc[i].get("symbols")
                            img = (
                                _images[0].get("o") or _images[0].get("url")
                                if _images
                                else None
                            )
                            if img is not None:
                                st.markdown(
                                    f"""
                                <div style='text-align: center;'>
                                    <img src='{img}' width='95%' />
                                </div>
                                <br>
                                """,
                                    unsafe_allow_html=True,
                                )
                            if text:
                                st.markdown(text, unsafe_allow_html=True)
                            if _url:
                                st.write(_url)

                        if st.session_state.selected_provider == "Tiingo":
                            _url = st.session_state.news.loc[i].get("url")
                            _tags = st.session_state.news.loc[i].get("tags")
                            _stocks = st.session_state.news.loc[i].get("symbols")
                            if _url:
                                st.write(_url)
                            st.divider()
                            if _tags:
                                st.markdown(
                                    f"##### Tags for this story:  \n {_tags}  \n"
                                )
                            if _stocks and _stocks is not nan:
                                st.markdown(f"##### Stocks mentioned:\n {_stocks}  \n")

            st.divider()
        st.write(
            "Learn more about the OpenBB Platform [here](https://docs.openbb.co/platform)"
        )


if __name__ == "__main__":
    main()
