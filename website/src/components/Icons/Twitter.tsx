import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const TwitterIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 16 14"
    width={16}
    height={14}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M14.115 2.481A3.36 3.36 0 0 0 15.56.618a6.472 6.472 0 0 1-2.085.817A3.229 3.229 0 0 0 9.532.778c-1.308.718-1.985 2.246-1.654 3.73C5.24 4.37 2.78 3.092 1.114.987c-.87 1.54-.426 3.507 1.015 4.497a3.208 3.208 0 0 1-1.486-.422v.042c0 1.604 1.102 2.985 2.634 3.302-.484.135-.99.155-1.483.058.431 1.372 1.663 2.31 3.067 2.339A6.48 6.48 0 0 1 0 12.199a9.12 9.12 0 0 0 5.032 1.513 9.157 9.157 0 0 0 6.623-2.787 9.644 9.644 0 0 0 2.716-6.795c0-.146-.003-.291-.01-.436A6.767 6.767 0 0 0 16 1.951a6.433 6.433 0 0 1-1.885.53Z"
      fill="currentColor"
    />
  </svg>
)

export default TwitterIcon
