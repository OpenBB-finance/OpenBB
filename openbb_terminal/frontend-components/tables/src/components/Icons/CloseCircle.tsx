import type { SVGProps } from "react";
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const CloseCircleIcon = ({
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
      d="M9 16.5a7.5 7.5 0 1 0 0-15 7.5 7.5 0 0 0 0 15ZM11.25 6.75l-4.5 4.5M6.75 6.75l4.5 4.5"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export default CloseCircleIcon;
