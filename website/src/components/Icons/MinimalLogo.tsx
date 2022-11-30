import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const MinimalLogoIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 255 127"
    width={255}
    height={127}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M151.404 103.189v-7.937h71.733v15.874h-71.733v-7.937Zm0-63.5v-7.937h87.66v15.874h-87.66V39.69Zm95.628-23.815H135.468V127h103.596V79.374h-87.66V63.5H255V15.874h-7.968Zm-215.16 87.315v-7.937h71.733v15.874H31.873v-7.937Zm-15.936-63.5v-7.937h87.66v15.874h-87.66V39.69ZM119.532 0v15.874H0V63.5h103.596v15.874h-87.66V127h103.596V15.874h15.936V0h-15.936Z"
      fill="currentColor"
    />
  </svg>
)

export default MinimalLogoIcon
