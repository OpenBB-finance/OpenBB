import type { SVGProps } from "react";
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const WarningIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 18 18"
    width={18}
    height={18}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M7.718 2.895 1.366 13.5a1.5 1.5 0 0 0 1.282 2.25h12.705a1.5 1.5 0 0 0 1.283-2.25L10.283 2.895a1.5 1.5 0 0 0-2.565 0v0ZM9 6.75v3M9 12.75h.008"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export default WarningIcon;
