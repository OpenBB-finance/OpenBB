import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const CommunityIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 28 24"
    width={28}
    height={24}
    fill="none"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M10 0a6.667 6.667 0 1 0 0 13.333A6.667 6.667 0 0 0 10 0ZM6 6.667a4 4 0 1 1 8 0 4 4 0 0 1-8 0Zm14.544.291a2.667 2.667 0 0 0-1.211-.291V4a5.333 5.333 0 1 1-3.143 9.643l-.001-.002 1.572-2.154a2.667 2.667 0 1 0 2.783-4.53ZM24.663 24a5.33 5.33 0 0 0-5.33-5.33V16a8.001 8.001 0 0 1 8 8h-2.67Zm-5.33 0h-2.667a6.667 6.667 0 0 0-13.333 0H.666a9.333 9.333 0 0 1 9.333-9.333A9.333 9.333 0 0 1 19.333 24Z"
      fill="currentColor"
    />
  </svg>
)

export default CommunityIcon
