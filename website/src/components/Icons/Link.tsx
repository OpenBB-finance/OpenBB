import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const LinkIcon = ({
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
      d="M8.465 20.535a5 5 0 0 1-3.536-8.536L7.05 9.878l1.414 1.413-2.121 2.121a3 3 0 0 0 4.243 4.243l2.12-2.12 1.415 1.415L12 19.07a4.969 4.969 0 0 1-3.536 1.465Zm.707-4.294-1.414-1.413 7.07-7.071 1.415 1.414-7.07 7.07h-.001Zm7.779-2.12-1.415-1.415 2.12-2.12a3 3 0 1 0-4.241-4.243l-2.122 2.12L9.879 7.05 12 4.928a5 5 0 0 1 7.07 7.07l-2.12 2.122Z"
      fill="currentColor"
    />
  </svg>
)

export default LinkIcon
