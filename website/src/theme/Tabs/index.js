import React, { cloneElement, useEffect } from "react";
import clsx from "clsx";
import {
  useScrollPositionBlocker,
  useTabs,
} from "@docusaurus/theme-common/internal";
import useIsBrowser from "@docusaurus/useIsBrowser";
import styles from "./styles.module.css";
import { useLocation } from "@docusaurus/router";
import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

function getOSName() {
  const userAgent = ExecutionEnvironment.canUseDOM ? navigator.userAgent : "";
  if (userAgent.indexOf("Windows") > -1) {
    return "Windows";
  } else if (userAgent.indexOf("Mac") > -1) {
    return "Mac";
  } else if (userAgent.indexOf("X11") > -1) {
    return "UNIX";
  } else if (userAgent.indexOf("Linux") > -1) {
    return "Linux";
  } else {
    return "Other";
  }
}

function getQueryVariable(query, variable) {
  // substring query
  const vars = query.substring(1).split("&");
  for (let i = 0; i < vars.length; i++) {
    let pair = vars[i].split("=");
    if (decodeURIComponent(pair[0]) == variable) {
      return decodeURIComponent(pair[1]);
    }
  }
  return null;
}

function getInstallationTabType() {
  const osName = getOSName();
  if (osName === "Windows") {
    return "windows";
  } else if (osName === "Mac") {
    return "mac";
  } else if (osName === "Linux" || osName === "UNIX") {
    return "python";
  }
  return "windows";
}

function TabList({ className, block, selectedValue, selectValue, tabValues }) {
  const tabRefs = [];
  const { blockElementScrollPositionUntilNextRender } =
    useScrollPositionBlocker();
  const { pathname, search } = useLocation();

  const handleTabChange = (event) => {
    const newTab = event.currentTarget;
    const newTabIndex = tabRefs.indexOf(newTab);
    const newTabValue = tabValues[newTabIndex].value;
    if (newTabValue !== selectedValue) {
      blockElementScrollPositionUntilNextRender(newTab);
      selectValue(newTabValue);
    }
  };

  if (ExecutionEnvironment.canUseDOM) {
    useEffect(() => {
      if (pathname.startsWith("/terminal/quickstart/installation")) {
        const value = getQueryVariable(search, "tab");
        const osTabValue = getInstallationTabType();
        selectValue(
          value
            ? ["mac", "windows", "python", "docker"].includes(value)
              ? value
              : osTabValue
            : osTabValue
        );
      }
    }, []);
  }

  const handleKeydown = (event) => {
    let focusElement = null;
    switch (event.key) {
      case "Enter": {
        handleTabChange(event);
        break;
      }
      case "ArrowRight": {
        const nextTab = tabRefs.indexOf(event.currentTarget) + 1;
        focusElement = tabRefs[nextTab] ?? tabRefs[0];
        break;
      }
      case "ArrowLeft": {
        const prevTab = tabRefs.indexOf(event.currentTarget) - 1;
        focusElement = tabRefs[prevTab] ?? tabRefs[tabRefs.length - 1];
        break;
      }
      default:
        break;
    }
    focusElement?.focus();
  };
  return (
    <ul
      role="tablist"
      aria-orientation="horizontal"
      className={clsx("_group-tab list-none -ml-7 my-6 overflow-auto")}
    >
      {tabValues.map(({ value, label, attributes }) => (
        <li
          // TODO extract TabListItem
          role="tab"
          tabIndex={selectedValue === value ? 0 : -1}
          aria-selected={selectedValue === value}
          key={value}
          ref={(tabControl) => tabRefs.push(tabControl)}
          onKeyDown={handleKeydown}
          onClick={handleTabChange}
          {...attributes}
          className={clsx(
            "font-bold tracking-widest w-fit px-3 inline-flex py-1 uppercase border-b text-lg cursor-pointer",
            styles.tabItem,
            attributes?.className,
            {
              "border-b-2 pointer-events-none": selectedValue === value,
              "border-b-2 text-[#669dcb] border-[#669dcb]":
                selectedValue === value && pathname.startsWith("/terminal"),
              "border-b-2 text-[#FB923C] border-[#FB923C]":
                selectedValue === value && pathname.startsWith("/sdk"),
              "border-grey-400 text-grey-400 hover:text-[#ffd4b1] hover:border-[#ffd4b1]":
                selectedValue !== value && pathname.startsWith("/sdk"),
              "border-grey-400 text-grey-400 hover:text-[#abd2f1] hover:border-[#abd2f1]":
                selectedValue !== value && pathname.startsWith("/terminal"),
            }
          )}
        >
          {label ?? value}
        </li>
      ))}
    </ul>
  );
}
function TabContent({ lazy, children, selectedValue }) {
  // eslint-disable-next-line no-param-reassign
  children = Array.isArray(children) ? children : [children];
  if (lazy) {
    const selectedTabItem = children.find(
      (tabItem) => tabItem.props.value === selectedValue
    );
    if (!selectedTabItem) {
      // fail-safe or fail-fast? not sure what's best here
      return null;
    }
    return cloneElement(selectedTabItem, { className: "margin-top--md" });
  }
  return (
    <div className="margin-top--md">
      {children.map((tabItem, i) =>
        cloneElement(tabItem, {
          key: i,
          hidden: tabItem.props.value !== selectedValue,
        })
      )}
    </div>
  );
}
function TabsComponent(props) {
  const tabs = useTabs(props);
  return (
    <div className={clsx("tabs-container", styles.tabList)}>
      <TabList {...props} {...tabs} />
      <TabContent {...props} {...tabs} />
    </div>
  );
}
export default function Tabs(props) {
  const isBrowser = useIsBrowser();
  return (
    <TabsComponent
      // Remount tabs after hydration
      // Temporary fix for https://github.com/facebook/docusaurus/issues/5653
      key={String(isBrowser)}
      {...props}
    />
  );
}
