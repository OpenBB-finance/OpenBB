import React, { SVGProps } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const VBIcon = ({
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
      d="M18.803 5c1.338.04 2.961.1 3.938 1.17.566.636.886 1.666.886 2.578 0 1.23-.533 1.924-.83 2.223-.378.395-.868.652-1.339.89.546.182 1.112.359 1.618.874.548.574.923 1.565.923 2.617a3.481 3.481 0 0 1-.923 2.458c-1.054 1.128-2.45 1.15-3.957 1.19H13v-2.858l1.187.02V7.835L13 7.856V5h5.803Zm-1.15 5.63c1.075.022 1.224.022 1.49-.04.62-.137 1.054-.727 1.022-1.394 0-.733-.399-1.147-.678-1.287-.277-.14-.493-.16-1.83-.18l-.004 2.9Zm0 5.512h1.038c.734 0 1.77-.017 1.77-1.347 0-.7-.36-1.17-.812-1.35-.32-.14-.468-.14-1.996-.14v2.837ZM0 5h5.87v2.856l-1.2-.02 1.994 8.011 2.153-8.01-1.2.019V5H13v2.856l-.911-.02L8.699 19H4.282L.854 7.836 0 7.856V5Z"
      fill="currentColor"
    />
  </svg>
)

export default VBIcon
