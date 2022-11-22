import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const GithubIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    width={15}
    height={16}
    viewBox="0 0 15 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M6 12.76c-3.333 1-3.333-1.667-4.667-2l4.667 2Zm4.667 2v-2.58a2.246 2.246 0 0 0-.627-1.74c2.094-.233 4.294-1.027 4.294-4.667 0-.93-.359-1.825-1-2.5a3.38 3.38 0 0 0-.06-2.513s-.787-.233-2.607.987a8.92 8.92 0 0 0-4.667 0C4.18.527 3.393.76 3.393.76a3.38 3.38 0 0 0-.06 2.513 3.627 3.627 0 0 0-1 2.52c0 3.614 2.2 4.407 4.294 4.667A2.248 2.248 0 0 0 6 12.18v2.58"
      fill="currentColor"
    />
    <path
      d="M10.667 14.76v-2.58a2.246 2.246 0 0 0-.627-1.74c2.094-.233 4.294-1.027 4.294-4.667 0-.93-.359-1.825-1-2.5a3.38 3.38 0 0 0-.06-2.513s-.787-.233-2.607.987a8.92 8.92 0 0 0-4.667 0C4.18.527 3.393.76 3.393.76a3.38 3.38 0 0 0-.06 2.513 3.627 3.627 0 0 0-1 2.52c0 3.614 2.2 4.407 4.294 4.667A2.248 2.248 0 0 0 6 12.18v2.58m0-2c-3.333 1-3.333-1.667-4.667-2l4.667 2Z"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

export default GithubIcon
