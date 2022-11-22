import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const DeepsourceIcon = ({
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
    <g clipPath="url(#aoooaoaooa)">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7.973 6.522h7.49c.308.004.6.122.817.33.216.207.339.486.342.779a1.089 1.089 0 0 1-.343.777c-.216.207-.509.324-.815.327H7.973V6.522Zm0 8.749h9.177c.306.003.599.12.815.326.217.207.34.486.343.778-.003.291-.126.57-.343.777-.216.206-.509.323-.815.326H7.973v-2.207ZM5 22.005V2.027h7.384a10.925 10.925 0 0 1 5.822 1.457 9.393 9.393 0 0 1 3.586 3.75 10.37 10.37 0 0 1 1.214 4.822 9.94 9.94 0 0 1-1.214 4.822 9.567 9.567 0 0 1-3.586 3.75 11.084 11.084 0 0 1-5.822 1.458H6.371c-.399-.107-1.349-.107-1.371-.107v.026ZM7.973 10.9h5.192c.308.001.602.118.82.325.217.206.34.486.344.779a1.095 1.095 0 0 1-.346.777c-.218.207-.51.324-.818.326H7.973V10.9Z"
        fill="currentColor"
      />
    </g>
    <defs>
      <clipPath id="aoooaoaooa">
        <path
          fill="currentColor"
          transform="translate(5 2)"
          d="M0 0h18v20H0z"
        />
      </clipPath>
    </defs>
  </svg>
)

export default DeepsourceIcon
