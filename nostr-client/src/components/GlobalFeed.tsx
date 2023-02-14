import { useRef } from "react";
import { useNostrEvents, dateToUnix } from "nostr-react";

const GlobalFeed = () => {
  const now = useRef(new Date()); // Make sure current time isn't re-rendered

  const { events } = useNostrEvents({
    filter: {
      since: dateToUnix(now.current), // all new events from now
      kinds: [1],
    },
  });

  return (
    <ul className="flex flex-col gap-2 max-w-sm mx-auto">
      {events.map((event) => (
        <li
          key={event.id}
          className="flex flex-col bg-gray-800/80 backdrop-blur backdrop-filter shadow-lg rounded-lg justify-between w-[320px] p-4"
        >
          <div className="flex items-center justify-between">
            <p className="font-semibold max-w-[100px] truncate">
              {event.pubkey}
            </p>
            <small className="text-sm">{event.created_at}</small>
          </div>
          <p className="text-sm">{event.content}</p>
        </li>
      ))}
    </ul>
  );
};

export default GlobalFeed;
