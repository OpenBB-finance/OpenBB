import React, { useState, useEffect, useRef } from "react";
import clsx from "clsx";
import { useThemeConfig, usePrismTheme } from "@docusaurus/theme-common";
import {
  parseCodeBlockTitle,
  parseLanguage,
  parseLines,
  containsLineNumbers,
  useCodeWordWrap,
} from "@docusaurus/theme-common/internal";
import Highlight, { defaultProps } from "prism-react-renderer";
import Line from "@theme/CodeBlock/Line";
import CopyButton from "@theme/CodeBlock/CopyButton";
import WordWrapButton from "@theme/CodeBlock/WordWrapButton";
import Container from "@theme/CodeBlock/Container";
import styles from "./styles.module.css";
import { useLocation } from "react-router-dom";

function getImageUrl(pathname, text) {
  if (!pathname.startsWith("/bot/")) {
    return null;
  }
  const pathvalue = pathname.split("/")[4];
  const platform = pathname.split("/")[3];
  let imgname = "c3m";
  if (
    (pathvalue == "charts" || pathvalue == "general") &&
    platform == "discord"
  ) {
    imgname = text.split(" ")[0].toLowerCase().replace("/", "");
  } else if (platform == "telegram") {
    console.log(pathvalue)
    if (pathvalue.toString() == "etf" || pathvalue.toString() == "screeners") {
      imgname = text.split(" ")[1].toLowerCase();
    } else {
      imgname = text.split(" ")[0].toLowerCase().replace("/", "");
    }
  } else {
    try {
      imgname = text.split(" ")[1].toLowerCase().replace("/", "");
      if (imgname == "defi") {
        imgname = text.split(" ")[2].toLowerCase().replace("/", "");
      }
    } catch (e) {
      imgname = text.split(" ")[0].toLowerCase().replace("/", "");
    }
  }

  const finalImage = `https://openbb-assets.s3.amazonaws.com/${platform}/${pathvalue}/${imgname}.png`;
  return finalImage;
}

export default function CodeBlockString({
  children,
  className: blockClassName = "",
  metastring,
  title: titleProp,
  showLineNumbers: showLineNumbersProp,
  language: languageProp,
}) {
  const [imageUrl, setImageUrl] = useState(null);
  const {
    prism: { defaultLanguage, magicComments },
  } = useThemeConfig();
  const language =
    languageProp ?? parseLanguage(blockClassName) ?? defaultLanguage;
  const prismTheme = usePrismTheme();
  const wordWrap = useCodeWordWrap();

  // We still parse the metastring in case we want to support more syntax in the
  // future. Note that MDX doesn't strip quotes when parsing metastring:
  // "title=\"xyz\"" => title: "\"xyz\""
  const title = parseCodeBlockTitle(metastring) || titleProp;
  const { lineClassNames, code } = parseLines(children, {
    metastring,
    language,
    magicComments,
  });
  const showLineNumbers =
    showLineNumbersProp ?? containsLineNumbers(metastring);

  const shouldWordwrapByDefault = metastring?.includes("wordwrap");

  const newDate = getThirdFriday();

  const newCode = code.replace("2022-07-29", newDate);
  const { pathname } = useLocation();

  // get Container sibling

  useEffect(() => {
    if (ref.current && pathname.startsWith("/bot/")) {
      // get ref.current sibling above
      const container = ref.current.parentElement;
      const containerSibling = container.previousElementSibling;
      if (containerSibling) {
        if (containerSibling.id.includes("examples")) {
          const finalImage = getImageUrl(pathname, newCode);
          setImageUrl(finalImage);
        }
      }
    }
  }, []);

  const ref = useRef(null);

  return (
    <>
      <Container
        as="div"
        className={clsx(
          blockClassName,
          language &&
            !blockClassName.includes(`language-${language}`) &&
            `language-${language}`
        )}
      >
        {title && <div className={styles.codeBlockTitle}>{title}</div>}
        <div className={styles.codeBlockContent} ref={ref}>
          <Highlight
            {...defaultProps}
            theme={prismTheme}
            code={newCode}
            language={language ?? "text"}
          >
            {({ className, tokens, getLineProps, getTokenProps }) => (
              <pre
                /* eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex */
                tabIndex={0}
                ref={wordWrap.codeBlockRef}
                className={clsx(className, styles.codeBlock, "thin-scrollbar")}
              >
                <code
                  style={
                    shouldWordwrapByDefault
                      ? {
                          whiteSpace: "pre-wrap",
                          overflowWrap: "anywhere",
                        }
                      : {}
                  }
                  className={clsx(
                    styles.codeBlockLines,
                    showLineNumbers && styles.codeBlockLinesWithNumbering
                  )}
                >
                  {tokens.map((line, i) => (
                    <Line
                      key={i}
                      line={line}
                      getLineProps={getLineProps}
                      getTokenProps={getTokenProps}
                      classNames={lineClassNames[i]}
                      showLineNumbers={showLineNumbers}
                    />
                  ))}
                </code>
              </pre>
            )}
          </Highlight>
          <div className={styles.buttonGroup}>
            {(wordWrap.isEnabled || wordWrap.isCodeScrollable) && (
              <WordWrapButton
                className={styles.codeButton}
                onClick={() => wordWrap.toggle()}
                isEnabled={wordWrap.isEnabled}
              />
            )}
            <CopyButton className={styles.codeButton} code={newCode} />
          </div>
        </div>
      </Container>
      {imageUrl && (
            <img width="70%" height="70%"
              onError={() => {
                setImageUrl(null);
              }}
              src={imageUrl}
              alt="example"
            />
          )}
    </>
  );
}

function getThirdFriday() {
  const thirdFriday = new Date();
  thirdFriday.setMonth(thirdFriday.getMonth() + 1);
  thirdFriday.setDate(1);
  const firstDay = thirdFriday.getDay();
  let daysToAdd = (5 - firstDay + 7) % 7;
  daysToAdd += 15;
  thirdFriday.setDate(daysToAdd);

  const yearString = thirdFriday.getFullYear().toString();
  const monthString = (thirdFriday.getMonth() + 1).toString().padStart(2, "0");
  const dayString = thirdFriday.getDate().toString().padStart(2, "0");
  const dateString = `${yearString}-${monthString}-${dayString}`;
  return dateString;
}
