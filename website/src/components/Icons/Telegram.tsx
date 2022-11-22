import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const TelegramIcon = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    viewBox="0 0 17 15"
    width={17}
    height={15}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M16.467.805a.382.382 0 0 0-.077-.168.341.341 0 0 0-.143-.106 1.12 1.12 0 0 0-.624.048S1.75 5.988.957 6.586c-.17.13-.22.206-.255.291-.137.427.29.616.29.616l3.576 1.264c.059.015.12.015.18 0 .814-.558 8.183-5.605 8.61-5.774.065-.022.116 0 .103.052-.172.649-6.573 6.819-6.573 6.819a.385.385 0 0 0-.04.071l-.332 3.847s-.14 1.178.946 0a30.835 30.835 0 0 1 1.88-1.865c1.23.92 2.553 1.94 3.123 2.471.096.1.21.179.334.231a.933.933 0 0 0 .391.072c.541-.021.693-.668.693-.668S16.412 2.978 16.496 1.5c0-.143.02-.238.02-.336a1.243 1.243 0 0 0-.049-.358Z"
      fill="currentColor"
    />
  </svg>
)

export default TelegramIcon
