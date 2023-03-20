import * as React from "react"
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const PlayIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 24 24"
    width={24}
    height={24}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="m5 3 14 9-14 9V3Z"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export default PlayIcon;
