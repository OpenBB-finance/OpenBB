import { SVGProps, Ref, forwardRef } from "react"
interface SVGRProps {
  title?: string
  titleId?: string
}

const SvgComponent = (
  { title, titleId, ...props }: SVGProps<SVGSVGElement> & SVGRProps,
  ref: Ref<SVGSVGElement>
) => (
  <svg
    viewBox="0 0 24 24"
    width={24}
    height={24}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    ref={ref}
    aria-labelledby={titleId}
    {...props}
  >
    {title ? <title id={titleId}>{title}</title> : null}
    <path
      d="M7 17 17 7M7 7h10v10"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

const ArrowTopRightIcon = forwardRef(SvgComponent)
export default ArrowTopRightIcon
