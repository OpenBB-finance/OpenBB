import React, { useState, cloneElement, isValidElement } from 'react';
import clsx from 'clsx';
import useIsBrowser from '@docusaurus/useIsBrowser';
import { duplicates } from '@docusaurus/theme-common';
import {
  useScrollPositionBlocker,
  useTabGroupChoice,
} from '@docusaurus/theme-common/internal';
import styles from './styles.module.css';
import { useLocation } from '@docusaurus/router';

function getQueryVariable(query, variable) {
  // substring query 
  const vars = query.substring(1).split('&');
  for (let i = 0; i < vars.length; i++) {
      let pair = vars[i].split('=');
      console.log(decodeURIComponent(pair[0]), variable)
      if (decodeURIComponent(pair[0]) == variable) {
          return decodeURIComponent(pair[1]);
      }
  }
  return null;
}

// A very rough duck type, but good enough to guard against mistakes while
// allowing customization
function isTabItem(comp) {
  return 'value' in comp.props;
}
function TabsComponent(props) {
  const {
    lazy,
    block,
    defaultValue: defaultValueProp,
    values: valuesProp,
    groupId,
    className,
  } = props;
  const children = React.Children.map(props.children, (child) => {
    if (isValidElement(child) && isTabItem(child)) {
      return child;
    }
    // child.type.name will give non-sensical values in prod because of
    // minification, but we assume it won't throw in prod.
    throw new Error(
      `Docusaurus error: Bad <Tabs> child <${
      // @ts-expect-error: guarding against unexpected cases
      typeof child.type === 'string' ? child.type : child.type.name
      }>: all children of the <Tabs> component should be <TabItem>, and every <TabItem> should have a unique "value" prop.`,
    );
  });
  const values =
    valuesProp ??
    // Only pick keys that we recognize. MDX would inject some keys by default
    children.map(({ props: { value, label, attributes } }) => ({
      value,
      label,
      attributes,
    }));
  const dup = duplicates(values, (a, b) => a.value === b.value);
  if (dup.length > 0) {
    throw new Error(
      `Docusaurus error: Duplicate values "${dup
        .map((a) => a.value)
        .join(', ')}" found in <Tabs>. Every value needs to be unique.`,
    );
  }
  // When defaultValueProp is null, don't show a default tab
  const defaultValue =
    defaultValueProp === null
      ? defaultValueProp
      : defaultValueProp ??
      children.find((child) => child.props.default)?.props.value ??
      children[0].props.value;
  if (defaultValue !== null && !values.some((a) => a.value === defaultValue)) {
    throw new Error(
      `Docusaurus error: The <Tabs> has a defaultValue "${defaultValue}" but none of its children has the corresponding value. Available values are: ${values
        .map((a) => a.value)
        .join(
          ', ',
        )}. If you intend to show no default tab, use defaultValue={null} instead.`,
    );
  }
  const { tabGroupChoices, setTabGroupChoices } = useTabGroupChoice();
  
  const { pathname, search } = useLocation()
  const value = getQueryVariable(search, 'tab')
  const [selectedValue, setSelectedValue] = useState(value ? value : defaultValue);
  const tabRefs = [];
  const { blockElementScrollPositionUntilNextRender } =
    useScrollPositionBlocker();
  if (groupId != null) {
    const relevantTabGroupChoice = tabGroupChoices[groupId];
    if (
      relevantTabGroupChoice != null &&
      relevantTabGroupChoice !== selectedValue &&
      values.some((value) => value.value === relevantTabGroupChoice)
    ) {
      setSelectedValue(relevantTabGroupChoice);
    }
  }
  const handleTabChange = (event) => {
    const newTab = event.currentTarget;
    const newTabIndex = tabRefs.indexOf(newTab);
    const newTabValue = values[newTabIndex].value;
    if (newTabValue !== selectedValue) {
      blockElementScrollPositionUntilNextRender(newTab);
      setSelectedValue(newTabValue);
      if (groupId != null) {
        setTabGroupChoices(groupId, String(newTabValue));
      }
    }
  };
  const handleKeydown = (event) => {
    let focusElement = null;
    switch (event.key) {
      case 'Enter': {
        handleTabChange(event);
        break;
      }
      case 'ArrowRight': {
        const nextTab = tabRefs.indexOf(event.currentTarget) + 1;
        focusElement = tabRefs[nextTab] ?? tabRefs[0];
        break;
      }
      case 'ArrowLeft': {
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
    <div>
      <ul
        role="tablist"
        aria-orientation="horizontal"
        className={clsx(
          '_group-tab list-none lg:-ml-7 my-6',
        )}>
        {values.map(({ value, label, attributes }) => (
          <li
            role="tab"
            tabIndex={selectedValue === value ? 0 : -1}
            aria-selected={selectedValue === value}
            key={value}
            ref={(tabControl) => tabRefs.push(tabControl)}
            onKeyDown={handleKeydown}
            onClick={handleTabChange}
            {...attributes}
            className={clsx(
              'font-bold tracking-widest w-fit px-3 inline-flex py-1 uppercase border-b text-lg cursor-pointer',
              styles.tabItem,
              attributes?.className,
              {
                'border-b-2 pointer-events-none': selectedValue === value,
                'border-b-2 text-[#669dcb] border-[#669dcb]': selectedValue === value && pathname.startsWith("/terminal"),
                'border-b-2 text-[#FB923C] border-[#FB923C]': selectedValue === value && pathname.startsWith("/sdk"),
                'border-grey-400 text-grey-400 hover:text-[#ffd4b1] hover:border-[#ffd4b1]': selectedValue !== value && pathname.startsWith("/sdk"),
                'border-grey-400 text-grey-400 hover:text-[#abd2f1] hover:border-[#abd2f1]': selectedValue !== value && pathname.startsWith("/terminal"),
              },
            )}>
            {label ?? value}
          </li>
        ))}
        <li className='w-full border-b border-grey-400 pointer-events-none py-1 mb-[12px]'></li>
      </ul>

      {lazy ? (
        cloneElement(
          children.filter(
            (tabItem) => tabItem.props.value === selectedValue,
          )[0],
          { className: 'margin-top--md' },
        )
      ) : (
        <div className="margin-top--md">
          {children.map((tabItem, i) =>
            cloneElement(tabItem, {
              key: i,
              hidden: tabItem.props.value !== selectedValue,
            }),
          )}
        </div>
      )}
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
