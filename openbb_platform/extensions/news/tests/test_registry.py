"""Registry tests."""

import pytest

from openbb_news import registry


def test_list_feeds_returns_defaults(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    feeds = registry.list_feeds()
    assert "pr_newswire_global" in feeds
    assert "bbc_world" in feeds
    assert feeds["bbc_world"].endswith("/world/rss.xml")


def test_list_feeds_user_override(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {"news": {"rss_feeds": {"my_feed": "https://my.test/rss"}}},
    )
    feeds = registry.list_feeds()
    assert feeds == {"my_feed": "https://my.test/rss"}


def test_list_feeds_ignores_non_dict_override(monkeypatch):
    monkeypatch.setattr(
        registry, "load_config", lambda: {"news": {"rss_feeds": ["not", "a", "dict"]}}
    )
    feeds = registry.list_feeds()
    assert "bbc_world" in feeds


def test_list_feeds_ignores_empty_override(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {"news": {"rss_feeds": {}}})
    feeds = registry.list_feeds()
    assert "bbc_world" in feeds


def test_get_feed_url_known():
    url = registry.get_feed_url("bbc_world")
    assert url.endswith("/world/rss.xml")


def test_get_feed_url_unknown_raises():
    with pytest.raises(ValueError, match="Unknown RSS feed source"):
        registry.get_feed_url("not_a_real_source")


def test_list_providers_default(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    providers = registry.list_providers()
    assert providers["axios"] == "Axios"
    assert providers["bbc"] == "BBC"
    assert providers["benzinga"] == "Benzinga"
    assert providers["cbc"] == "CBC"
    assert providers["drudge_report"] == "Drudge Report"
    assert providers["fox_news"] == "Fox News"
    assert providers["fortune"] == "Fortune"
    assert providers["globenewswire"] == "GlobeNewswire"
    assert providers["google_news"] == "Google News"
    assert providers["pr_newswire"] == "PR Newswire"
    assert providers["yahoo_finance"] == "Yahoo Finance"
    assert providers["wired"] == "Wired"
    assert "custom" not in providers
    assert "barchart" not in providers
    assert "cnn" not in providers
    assert "seeking_alpha" not in providers


def test_get_feed_url_drudge_report():
    assert (
        registry.get_feed_url("drudge_report")
        == "http://feeds.feedburner.com/DrudgeReportFeed"
    )


def test_list_feed_choices_cbc(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("cbc")
    labels = [c["label"] for c in choices]
    assert "Business" in labels
    assert "World" in labels
    assert "Region — Toronto" in labels
    assert "Sports — NHL" in labels
    assert labels == sorted(labels)


def test_get_feed_url_cbc_business():
    assert (
        registry.get_feed_url("cbc_business")
        == "https://www.cbc.ca/webfeed/rss/rss-business"
    )


def test_list_feed_choices_benzinga(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("benzinga")
    labels = [c["label"] for c in choices]
    assert "Markets" in labels
    assert "Cryptocurrency" in labels
    assert "Latest" in labels
    assert labels == sorted(labels)


def test_list_feed_choices_globenewswire(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("globenewswire")
    labels = [c["label"] for c in choices]
    assert "All News" in labels
    assert "United States" in labels
    assert "Industry — Energy" in labels
    assert "Industry — Financials" in labels
    assert "Industry — Banks" in labels
    assert "Industry — Pharmaceuticals" in labels
    assert "Industry — Gold Mining" in labels
    assert "Industry — Semiconductors" in labels
    assert "Industry — Diversified REITs" in labels
    assert "Subject — Earnings Releases and Operating Results" in labels
    assert "Subject — Dividend Reports and Estimates" in labels
    assert "Subject — Mergers and Acquisitions" in labels
    assert len(choices) == 253
    assert labels == sorted(labels)


def test_get_feed_url_globenewswire_all():
    url = registry.get_feed_url("globenewswire_all")
    assert url.startswith("https://www.globenewswire.com/RssFeed/")
    assert "AllNews" in url


def test_get_feed_url_globenewswire_industry():
    url = registry.get_feed_url("globenewswire_energy")
    assert url.startswith(
        "https://www.globenewswire.com/AtomFeed/industry/1/feedTitle/"
    )
    assert "Energy" in url


def test_globenewswire_industry_key_helper():
    assert (
        registry._globenewswire_industry_key("Iron and Steel")
        == "globenewswire_iron_and_steel"
    )
    assert (
        registry._globenewswire_industry_key(
            "Building, Roofing, Wallboard and Plumbing"
        )
        == "globenewswire_building_roofing_wallboard_and_plumbing"
    )
    assert (
        registry._globenewswire_industry_key("REITs & Real Estate")
        == "globenewswire_reits_and_real_estate"
    )


def test_globenewswire_industries_unique_keys():
    keys = [
        registry._globenewswire_industry_key(label)
        for _code, label in registry._GLOBENEWSWIRE_INDUSTRIES
    ]
    assert len(keys) == len(set(keys))


def test_get_feed_url_globenewswire_subject():
    url = registry.get_feed_url(
        "globenewswire_subject_earnings_releases_and_operating_results"
    )
    assert url.startswith(
        "https://www.globenewswire.com/AtomFeed/subjectcode/13/feedTitle/"
    )
    assert "Earnings" in url


def test_globenewswire_subject_key_helper():
    assert (
        registry._globenewswire_subject_key("Insider's Buy, Sell")
        == "globenewswire_subject_insiders_buy_sell"
    )
    assert (
        registry._globenewswire_subject_key("Mergers and Acquisitions")
        == "globenewswire_subject_mergers_and_acquisitions"
    )


def test_globenewswire_subjects_unique_keys():
    keys = [
        registry._globenewswire_subject_key(label)
        for _code, label in registry._GLOBENEWSWIRE_SUBJECTS
    ]
    assert len(keys) == len(set(keys))


def test_get_feed_url_benzinga_markets():
    assert (
        registry.get_feed_url("benzinga_markets")
        == "https://www.benzinga.com/markets/feed"
    )


def test_list_feed_choices_google_news(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("google_news")
    labels = [c["label"] for c in choices]
    assert "Business" in labels
    assert "Technology" in labels
    assert "Top — US" in labels
    assert "Top — Canada" in labels
    assert labels == sorted(labels)


def test_get_feed_url_google_news_us():
    assert (
        registry.get_feed_url("google_news_us")
        == "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    )


def test_default_feed_for_curated_picks(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    expected = {
        "axios": "axios_main",
        "bbc": "bbc_world",
        "benzinga": "benzinga_markets",
        "cbc": "cbc_business",
        "fox_news": "fox_news_latest",
        "globenewswire": "globenewswire_all",
        "google_news": "google_news_us",
        "pr_newswire": "pr_newswire_global",
        "wired": "wired_business",
    }
    for provider, feed_key in expected.items():
        assert registry.default_feed_for(provider) == feed_key


def test_default_feed_for_falls_back_to_first_alphabetical(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    assert registry.default_feed_for("fortune") == "fortune"


def test_curated_defaults_reference_real_feeds(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    feeds = registry.list_feeds()
    for provider, feed_key in registry._DEFAULT_FEED_BY_PROVIDER.items():
        assert feed_key in feeds, f"{provider} default {feed_key!r} missing"


def test_every_multi_feed_provider_has_a_curated_default(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    for provider in registry.list_providers():
        if provider == "custom":
            continue
        choices = registry.list_feed_choices(provider)
        if len(choices) > 1:
            assert provider in registry._DEFAULT_FEED_BY_PROVIDER, (
                f"multi-feed provider {provider!r} needs a curated default"
            )


def test_default_feed_for_unknown_provider(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    assert registry.default_feed_for("totally_made_up") is None


def test_default_feed_for_empty_provider():
    assert registry.default_feed_for(None) is None
    assert registry.default_feed_for("") is None


def test_default_feed_for_drops_stale_curated_default(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {"news": {"rss_feeds": {"only_one": "https://x.test/rss"}}},
    )
    assert registry.default_feed_for("axios") is None
    assert registry.default_feed_for("custom") == "only_one"


def test_list_feed_choices_axios(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("axios")
    assert choices == [{"label": "Latest", "value": "axios_main"}]


def test_get_feed_url_axios_main():
    assert registry.get_feed_url("axios_main") == "https://api.axios.com/feed/"


def test_list_feed_choices_wired(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("wired")
    labels = [c["label"] for c in choices]
    assert "Latest" in labels
    assert "Backchannel" in labels
    assert "Business" in labels
    assert "Culture" in labels
    assert "Gear" in labels
    assert "Ideas" in labels
    assert "Science" in labels
    assert "Security" in labels
    assert "Tag — AI" in labels
    assert "Tag — Wired Guide" in labels
    assert len(choices) == 10
    assert labels == sorted(labels)


def test_get_feed_url_wired_main():
    assert registry.get_feed_url("wired_main") == "https://www.wired.com/feed/rss"


def test_get_feed_url_wired_business():
    assert (
        registry.get_feed_url("wired_business")
        == "https://www.wired.com/feed/category/business/latest/rss"
    )


def test_list_providers_user_feeds_are_custom(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {"news": {"rss_feeds": {"my_feed": "https://my.test/rss"}}},
    )
    providers = registry.list_providers()
    assert providers == {"custom": "Custom"}


def test_list_feed_choices_filters_by_provider(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    bbc = registry.list_feed_choices("bbc")
    labels = [c["label"] for c in bbc]
    assert "World" in labels
    assert "Politics" in labels
    assert "Technology" in labels
    assert labels == sorted(labels)
    fox = registry.list_feed_choices("fox_news")
    fox_labels = [c["label"] for c in fox]
    assert "Latest Headlines" in fox_labels
    assert "Politics" in fox_labels


def test_list_feed_choices_pr_newswire(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    choices = registry.list_feed_choices("pr_newswire")
    labels = [c["label"] for c in choices]
    assert "Global" in labels
    assert "APAC — General Business" in labels
    assert "APAC (Chinese)" in labels
    assert labels == sorted(labels)


def test_list_feed_choices_no_provider(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    assert registry.list_feed_choices(None) == []
    assert registry.list_feed_choices("") == []


def test_list_feed_choices_unknown_provider(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: {})
    assert registry.list_feed_choices("totally_made_up") == []


def test_list_feed_choices_custom_feeds(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {"news": {"rss_feeds": {"my_feed": "https://my.test/rss"}}},
    )
    choices = registry.list_feed_choices("custom")
    assert choices == [{"label": "My Feed", "value": "my_feed"}]


def test_user_feeds_rich_form_with_provider_and_label(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_feeds": {
                    "alpha": {
                        "url": "https://alpha.test/rss",
                        "provider": "internal",
                        "label": "Alpha Research",
                    },
                    "beta": {
                        "url": "https://beta.test/rss",
                        "provider": "internal",
                        "label": "Beta Research",
                    },
                }
            }
        },
    )
    feeds = registry.list_feeds()
    assert feeds == {
        "alpha": "https://alpha.test/rss",
        "beta": "https://beta.test/rss",
    }
    choices = registry.list_feed_choices("internal")
    assert {c["value"] for c in choices} == {"alpha", "beta"}
    labels = {c["label"] for c in choices}
    assert labels == {"Alpha Research", "Beta Research"}


def test_user_provider_labels_apply(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_providers": {"internal": "Internal Sources"},
                "rss_feeds": {
                    "x": {"url": "https://x.test/rss", "provider": "internal"},
                },
            }
        },
    )
    providers = registry.list_providers()
    assert providers == {"internal": "Internal Sources"}


def test_user_provider_unknown_id_falls_back_to_humanized(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_feeds": {
                    "x": {"url": "https://x.test/rss", "provider": "acme_research"},
                },
            }
        },
    )
    providers = registry.list_providers()
    assert providers == {"acme_research": "Acme Research"}


def test_user_feeds_merge_defaults_preserves_bundled(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "merge_defaults": True,
                "rss_feeds": {"x": "https://x.test/rss"},
            }
        },
    )
    feeds = registry.list_feeds()
    assert "bbc_world" in feeds
    assert "pr_newswire_global" in feeds
    assert feeds["x"] == "https://x.test/rss"
    providers = registry.list_providers()
    assert "bbc" in providers
    assert "custom" in providers


def test_user_feeds_merge_override_replaces_bundled_key(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "merge_defaults": True,
                "rss_feeds": {"bbc_world": "https://my.test/bbc"},
            }
        },
    )
    feeds = registry.list_feeds()
    assert feeds["bbc_world"] == "https://my.test/bbc"


def test_user_feeds_rich_form_ignores_missing_url(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_feeds": {
                    "good": {"url": "https://good.test/rss"},
                    "bad": {"provider": "internal"},
                    "also_bad": 42,
                }
            }
        },
    )
    feeds = registry.list_feeds()
    assert feeds == {"good": "https://good.test/rss"}


def test_user_feeds_rich_form_default_provider_is_custom(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_feeds": {
                    "x": {"url": "https://x.test/rss", "label": "Pretty Label"},
                }
            }
        },
    )
    providers = registry.list_providers()
    assert providers == {"custom": "Custom"}
    choices = registry.list_feed_choices("custom")
    assert choices == [{"label": "Pretty Label", "value": "x"}]


def test_load_config_returning_non_dict_falls_back_to_defaults(monkeypatch):
    monkeypatch.setattr(registry, "load_config", lambda: None)
    feeds = registry.list_feeds()
    assert "bbc_world" in feeds


def test_user_provider_labels_ignores_non_string_values(monkeypatch):
    monkeypatch.setattr(
        registry,
        "load_config",
        lambda: {
            "news": {
                "rss_providers": {"internal": 42},
                "rss_feeds": {
                    "x": {"url": "https://x.test/rss", "provider": "internal"},
                },
            }
        },
    )
    providers = registry.list_providers()
    assert providers == {"internal": "Internal"}


def test_slug_helper():
    assert registry._slug("apac/zh") == "apac_zh"
    assert registry._slug("business-technology") == "business_technology"


def test_humanize_helper():
    assert registry._humanize("my_internal_feed") == "My Internal Feed"


def test_default_meta_covers_every_feed():
    assert set(registry._DEFAULT_FEEDS) == set(registry._DEFAULT_META)
    for entry in registry._DEFAULT_META.values():
        assert entry["provider"]
        assert entry["label"]
