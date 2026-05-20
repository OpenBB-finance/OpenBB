# openbb-news

RSS news feeds for the OpenBB Platform — one Workspace Newsfeed widget backed by
a registry of 400+ vetted feeds (Benzinga, GlobeNewswire by full ICB industry
breakdown + subject/event-type breakdown — earnings, M&A, dividends, IPOs, etc.,
PR Newswire regional + category, Axios, Yahoo Finance, Fortune, BBC, Fox News,
Drudge Report, Google News regional + topic). The widget defaults to
**Benzinga → Markets** so it loads finance-relevant articles immediately on
first open.

## Install

```bash
uv pip install -e .
```

## Endpoints

| GET path | Returns |
| --- | --- |
| `/api/v1/news/rss?outlet=<id>&source=<key>&limit=<n>&fetch_body=<bool>` | `OBBject[list[NewsItemData]]` — `{title, date, author, url, excerpt, body}` per article. Empty when `source` is unset and no default can be resolved. |
| `/api/v1/news/rss_providers` | `list[{label, value}]` — drives the widget's **Provider** dropdown. |
| `/api/v1/news/rss_feeds?outlet=<id>` | `list[{label, value}]` — drives the widget's **Feed** dropdown, filtered by the selected provider. |

`fetch_body=true` extracts the full article body from each entry's URL via
JSON-LD `articleBody` first, then the largest `<article>` element after
stripping site chrome (`nav`/`header`/`footer`/`aside`/`script`/`style`/`form`/
`iframe`/`button`/`svg`). Requires at least two real `<p>` paragraphs and
rejects pages whose body contains unrendered template markers (`[[`, `{{`);
falls back to the RSS summary on any miss. Bounded `lru_cache(maxsize=256)`
keeps repeat fetches in-process; no disk persistence.

## Pluggable feeds — `openbb.toml`

Three levers in `~/.openbb_platform/openbb.toml`, all under `[news]`:

### 1. Add or replace feeds — `[news.rss_feeds]`

**Simple form** — `key = "url-string"`. The feed appears under a single
"Custom" provider; the label is a humanized form of the key.

```toml
[news.rss_feeds]
my_internal = "https://internal.example.com/news.rss"
acme_blog   = "https://acme.example.com/feed"
```

**Rich form** — `key = { url, provider, label }` (or the equivalent table
syntax). Lets you bucket feeds into your own provider and give them a
display label, so the widget's Provider → Feed cascade groups them.

```toml
[news.rss_feeds.alpha_research]
url      = "https://alpha.example.com/rss"
provider = "acme_research"
label    = "Alpha Research"

[news.rss_feeds.beta_research]
url      = "https://acme.example.com/beta/rss"
provider = "acme_research"
label    = "Beta Research"
```

### 2. Pretty provider names — `[news.rss_providers]`

By default a provider id is humanized (`acme_research` → "Acme Research"). To
control the display label exactly, map provider id → label:

```toml
[news.rss_providers]
acme_research = "Acme Research"
internal      = "Internal Sources"
```

### 3. Keep the bundled defaults — `[news] merge_defaults`

Without this flag, the presence of any `[news.rss_feeds]` entries replaces
the 438 bundled feeds entirely. Set `merge_defaults = true` to keep
everything and add your feeds on top. User keys that collide with bundled
keys override the bundled URL.

```toml
[news]
merge_defaults = true

[news.rss_feeds]
my_internal = "https://internal.example.com/news.rss"
```

### Full example

```toml
[news]
merge_defaults = true

[news.rss_providers]
acme_research = "Acme Research"

[news.rss_feeds.alpha]
url      = "https://alpha.example.com/rss"
provider = "acme_research"
label    = "Alpha Research"

[news.rss_feeds.beta]
url      = "https://beta.example.com/rss"
provider = "acme_research"
label    = "Beta Research"
```

The Workspace Newsfeed widget rebuilds its **Provider** + **Feed** dropdowns
from this config on each request — restart the server only if the file was
empty at boot.

## Tests

```bash
pytest tests --cov=openbb_news --cov-fail-under=100
pytest integration -m integration   # hits the live feeds
```
