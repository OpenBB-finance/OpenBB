import type { NewsItem } from "../../lib/watchlistApi";

interface NewsItemCardProps {
  item: NewsItem;
  showTime?: boolean;
}

function formatTime(isoDate: string): string {
  try {
    const date = new Date(isoDate);
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      timeZoneName: "short",
    });
  } catch {
    return "";
  }
}

export function NewsItemCard({ item, showTime = true }: NewsItemCardProps) {
  if (item.is_breaking) {
    return (
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block rounded-sm bg-red-600/90 px-3 py-2 transition-colors hover:bg-red-600"
      >
        <div className="flex items-center gap-2">
          {showTime && (
            <span className="body-xxs-medium text-red-100 opacity-70">
              {formatTime(item.published_at)}
            </span>
          )}
          <span className="body-xs-medium text-white uppercase">{item.title}</span>
        </div>
      </a>
    );
  }

  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-sm px-3 py-2 transition-colors hover:bg-theme-secondary/60"
    >
      <div className="flex items-start gap-2">
        {showTime && (
          <span className="body-xxs-regular text-theme-muted whitespace-nowrap pt-0.5">
            {formatTime(item.published_at)}
          </span>
        )}
        <div className="min-w-0 flex-1">
          <p className="body-xs-medium text-theme-primary leading-snug">{item.title}</p>
          {item.summary && item.summary !== item.title && (
            <p className="mt-1 body-xxs-regular text-theme-muted line-clamp-2">{item.summary}</p>
          )}
          <p className="mt-1 body-xxs-regular text-theme-muted opacity-60">{item.source}</p>
        </div>
      </div>
    </a>
  );
}
