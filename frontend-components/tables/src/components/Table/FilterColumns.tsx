import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { CheckIcon, ChevronDownIcon } from "@radix-ui/react-icons";
import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import { useEffect, useRef, useState } from "react";
import useOnClickOutside from "../../utils/useClickOutside";
import clsx from "clsx";

export default function FilterColumns({
  label,
  table,
}: {
  label: string;
  table: any;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useOnClickOutside(ref, () => setOpen(false));

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <DropdownMenuPrimitive.Root open={open}>
      <DropdownMenuPrimitive.Group className="flex flex-row items-center gap-2 text-sm">
        <DropdownMenuPrimitive.Label className="whitespace-nowrap">
          {label}
        </DropdownMenuPrimitive.Label>
        <DropdownMenuPrimitive.Trigger
          onClick={() => setOpen(!open)}
          className="bg-white dark:bg-grey-900 whitespace-nowrap h-[36px] border-[1.5px] border-grey-700 rounded p-3 inline-flex items-center justify-center leading-none gap-[5px] shadow-[0_2px_10px] shadow-black/10 focus:shadow-[0_0_0_2px] focus:shadow-black data-[placeholder]:text-white outline-none"
          aria-label={label}
        >
          <span>Filter columns</span>
          <ChevronDownIcon
            className={clsx({
              "transform rotate-180 duration-200 transition": open,
            })}
          />
        </DropdownMenuPrimitive.Trigger>
      </DropdownMenuPrimitive.Group>
      <DropdownMenuPrimitive.Portal>
        <DropdownMenuPrimitive.Content
          sideOffset={10}
          ref={ref}
          className="z-50 bg-white/80 dark:bg-grey-900/80 backdrop-filter backdrop-blur flex flex-col gap-4 overflow-auto border-[1.5px] border-grey-700 rounded p-3 max-h-[500px]  text-black dark:text-white"
        >
          <DropdownMenuPrimitive.Item>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={table.getIsAllColumnsVisible()}
                onChange={table.getToggleAllColumnsVisibilityHandler()}
              />
              Toggle All
            </label>
          </DropdownMenuPrimitive.Item>
          {table
            .getAllLeafColumns()
            .filter((column: any) => column.id !== "select")
            .map((column: any) => {
              return (
                <DropdownMenuPrimitive.Item key={column.id}>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={column.getIsVisible()}
                      onChange={column.getToggleVisibilityHandler()}
                    />
                    {column.id}
                  </label>
                </DropdownMenuPrimitive.Item>
              );
            })}
        </DropdownMenuPrimitive.Content>
      </DropdownMenuPrimitive.Portal>
    </DropdownMenuPrimitive.Root>
  );
}

/*
              <div className="p-2 border border-black shadow rounded grid grid-cols-4">
              <div className="px-1 border-b border-black">
              <label>
              <input
              type="checkbox"
              checked={table.getIsAllColumnsVisible()}
              onChange={table.getToggleAllColumnsVisibilityHandler()}
              className="mr-1"
              />
              Toggle All
              </label>
              </div>
                {table.getAllLeafColumns().map((column) => {
                  return (
                    <div key={column.id} className="px-1">
                    <label>
                    <input
                    type="checkbox"
                    checked={column.getIsVisible()}
                    onChange={column.getToggleVisibilityHandler()}
                    className="mr-1"
                    />
                    {column.id}
                      </label>
                    </div>
                  );
                })}
              </div>
              */
