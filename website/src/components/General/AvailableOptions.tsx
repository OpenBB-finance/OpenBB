import * as DialogPrimitive from "@radix-ui/react-dialog";
import React, { useState } from "react";
import CloseIcon from "../Icons/Close";
import Fuse from "fuse.js";

//TODO - Make this show up nicer - Doesn't look like it does on bot site
export default function AvailableOptions({
  label,
  allOptions,
}: {
  label: string;
  allOptions: string[];
}) {
  const [options, setOptions] = useState(allOptions);
  const fuse = new Fuse(allOptions, {
    threshold: 0,
    distance: 0,
  });

  function searchWithFuse(query: string) {
    if (!query) {
      return [];
    }

    return fuse.search(query).map((result) => result.item);
  }
  return (
    <DialogPrimitive.Root
      onOpenChange={(value) => {
        if (!value) {
          setOptions(allOptions);
        }
      }}
    >
      <DialogPrimitive.Trigger className="_btn sm:w-fit mb-10 text-sm ml-4">
        See {label}
      </DialogPrimitive.Trigger>
      <DialogPrimitive.Overlay className="_modal-overlay" />
      <DialogPrimitive.Content className="_modal">
        <DialogPrimitive.Close
          tabIndex={-1}
          className="absolute top-[40px] right-[46px] text-grey-200 hover:text-white rounded-[4px] focus:outline focus:outline-2 focus:outline-grey-500"
        >
          <CloseIcon className="w-6 h-6" />
        </DialogPrimitive.Close>
        <DialogPrimitive.Title className="_modal-title">
          {label}
        </DialogPrimitive.Title>
        <DialogPrimitive.Description className="mt-6 text-grey-200 text-sm">
          Search for {label}
        </DialogPrimitive.Description>
        <div className="mt-10 w-full">
          <div className="relative">
            <input
              onChange={(e) => {
                const query = e.target.value;
                if (query) setOptions(searchWithFuse(e.target.value));
                else setOptions(allOptions);
              }}
              required
              placeholder=" "
              type="text"
              className="input peer"
              id="search-input"
            />
            <label htmlFor="search-input" className="_floating-label">
              {label}
            </label>
          </div>
          <ul className="h-40 mt-8 space-y-4 text-grey-400 text-sm">
            {options.slice(0, 5).map((option) => (
              <li key={option}>{option}</li>
            ))}
          </ul>
          <div className="_divider my-8" />
          <p className="mt-4 text-grey-500 text-sm">{`${options.length} ${label} found`}</p>
        </div>
      </DialogPrimitive.Content>
    </DialogPrimitive.Root>
  );
}
