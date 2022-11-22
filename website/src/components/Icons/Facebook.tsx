import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const FacebookIcon = ({
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
      d="M2.002 12.002a10.005 10.005 0 0 0 8.437 9.88v-6.99H7.902v-2.89h2.54v-2.2a3.528 3.528 0 0 1 3.773-3.9c.75.013 1.5.08 2.24.2v2.46h-1.264a1.446 1.446 0 0 0-1.628 1.563v1.877h2.771l-.443 2.891h-2.328v6.988a10 10 0 1 0-11.561-9.879Z"
      fill="currentColor"
    />
  </svg>
)

export default FacebookIcon
