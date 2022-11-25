import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const FbSmallIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 11 20"
    width={11}
    height={20}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M11 0H8a5 5 0 0 0-5 5v3H0v4h3v8h4v-8h3l1-4H7V5a1 1 0 0 1 1-1h3V0Z"
      fill="currentColor"
    />
  </svg>
)

export default FbSmallIcon
