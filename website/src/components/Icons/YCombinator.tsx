import * as React from "react"
import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const YCombinatorIcon = ({
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
    <g clipPath="url(#a231321312)">
      <path
        d="M5 3.007h3.803c.205 0 .287.096.375.254.908 1.642 1.819 3.28 2.733 4.916l.196.34c.161-.052.185-.198.246-.307.94-1.635 1.876-3.274 2.807-4.914a.502.502 0 0 1 .504-.29c1.104.014 2.208 0 3.327 0 .025.178-.096.278-.164.392a4184.326 4184.326 0 0 1-4.872 8.048c-.12.193-.18.417-.173.645 0 2.854 0 5.71.009 8.565 0 .267-.046.348-.324.343-.95-.02-1.903-.02-2.854 0-.277 0-.35-.067-.349-.353.012-2.855 0-5.71.01-8.565a1.126 1.126 0 0 0-.17-.61C8.464 8.77 6.828 6.065 5.195 3.36c-.055-.1-.11-.204-.195-.354Z"
        fill="currentColor"
      />
    </g>
    <defs>
      <clipPath id="a231321312">
        <path
          fill="currentColor"
          transform="translate(5 3)"
          d="M0 0h14v18H0z"
        />
      </clipPath>
    </defs>
  </svg>
)

export default YCombinatorIcon
