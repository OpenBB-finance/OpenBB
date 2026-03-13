import * as SelectPrimitive from "@radix-ui/react-select";
import {
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from "@radix-ui/react-icons";
import { forwardRef } from "react";
import clsx from "clsx";

const Select = ({
  value,
  onChange,
  label = "Select",
  placeholder = "Select a fruit…",
  groups,
  labelType = "col",
}: {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  labelType?: "col" | "row";
  groups: {
    label: string;
    items: {
      label: string;
      value: string | number;
      disabled?: boolean;
    }[];
  }[];
}) => {
  const onlyOneGroup = groups?.length === 1;
  return (
    <SelectPrimitive.Root value={value} onValueChange={onChange}>
      <SelectPrimitive.Group
        className={clsx("flex gap-1", {
          "flex-row items-center gap-2": labelType === "row",
          "flex-col": labelType === "col",
        })}
      >
        <SelectPrimitive.Label className="whitespace-nowrap">
          {label}
        </SelectPrimitive.Label>
        <SelectPrimitive.Trigger
          className="justify-between bg-white text-black dark:text-white dark:bg-grey-900 whitespace-nowrap h-[36px] border-[1.5px] border-grey-700 rounded p-3 inline-flex items-center leading-none gap-[5px] shadow-[0_2px_10px] shadow-black/10 focus:shadow-[0_0_0_2px] focus:shadow-black data-[placeholder]:text-white outline-none"
          aria-label={label}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon>
            <ChevronDownIcon />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
      </SelectPrimitive.Group>
      <SelectPrimitive.Portal>
        <SelectPrimitive.Content className="z-50 bg-white/80 dark:bg-grey-900/80 backdrop-filter backdrop-blur overflow-hidden border-[1.5px] border-grey-700 rounded p-3 shadow-[0px_10px_38px_-10px_rgba(22,_23,_24,_0.35),0px_10px_20px_-15px_rgba(22,_23,_24,_0.2)]">
          <SelectPrimitive.ScrollUpButton className="flex items-center justify-center h-[25px] cursor-default dark:text-white text-black">
            <ChevronUpIcon />
          </SelectPrimitive.ScrollUpButton>
          <SelectPrimitive.Viewport className="p-[5px]">
            {onlyOneGroup ? (
              <SelectPrimitive.Group>
                {groups[0].items.map((item) => (
                  //@ts-ignore
                  <SelectItem value={item.value} disabled={item.disabled}>
                    {item.label}
                  </SelectItem>
                ))}
              </SelectPrimitive.Group>
            ) : (
              groups.map((group, idx) => (
                <SelectPrimitive.Group key={group.label}>
                  <SelectPrimitive.Label className="text-xs leading-[25px]">
                    {group.label}
                  </SelectPrimitive.Label>
                  {group.items.map((item) => (
                    //@ts-ignore
                    <SelectItem
                      key={item.value}
                      value={item.value}
                      disabled={item.disabled}
                    >
                      {item.label}
                    </SelectItem>
                  ))}
                </SelectPrimitive.Group>
              ))
            )}
          </SelectPrimitive.Viewport>
          <SelectPrimitive.ScrollDownButton className="flex items-center justify-center h-[25px] cursor-default dark:text-white text-black">
            <ChevronDownIcon />
          </SelectPrimitive.ScrollDownButton>
        </SelectPrimitive.Content>
      </SelectPrimitive.Portal>
    </SelectPrimitive.Root>
  );
};

const SelectItem = forwardRef(
  //@ts-ignore
  ({ children, className, ...props }, forwardedRef) => {
    return (
      <SelectPrimitive.Item
        className={clsx(
          "text-[13px] leading-none rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[disabled]:text-grey-400 data-[disabled]:pointer-events-none data-[highlighted]:outline-none data-[highlighted]:bg-grey-600 data-[highlighted]:text-white  text-black dark:text-white",
          className
        )}
        {...props}
        //@ts-ignore
        ref={forwardedRef}
      >
        <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
        <SelectPrimitive.ItemIndicator className="absolute left-0 w-[25px] inline-flex items-center justify-center">
          <CheckIcon />
        </SelectPrimitive.ItemIndicator>
      </SelectPrimitive.Item>
    );
  }
);

export default Select;
