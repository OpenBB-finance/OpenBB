import React, { SVGProps } from "react";
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const OnlyPlatformLetteringLogo = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    width="110"
    height="9"
    viewBox="0 0 110 9"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fill="#fff"
      d="M8.333.398H.885V8.9h1.064V5.71h7.448V.391H8.333v.007Zm0 1.595v2.66H1.949V1.46h6.384v.532ZM15.397.392h1.079v7.55h6.471v.934h-7.55V.393ZM36.395.398h-7.448V8.9h1.064V5.71h6.384v3.19h1.064V.39h-1.064v.007Zm0 4.255h-6.384V1.46h6.384v3.192Z"
    />
    <path
      fill="#fff"
      fillRule="evenodd"
      d="M43.46.392V1.47h3.703v7.407h1.078V1.47h3.703V.392H43.46Z"
      clipRule="evenodd"
    />
    <path
      fill="#fff"
      d="M65.377.392h1.062v1.06H59.008V4.634h6.9v1.06H59.008V8.877h-1.064V.392H65.377ZM79.887.392h-7.448v8.503h8.513V.392h-1.065Zm0 1.594v5.846h-6.386V1.454h6.386v.532ZM94.403 8.902l-1.945-3.348h1.064l1.944 3.348h-1.063Z"
    />
    <path
      fill="#fff"
      d="M94.4.398h-7.448V8.9h1.064V5.71h7.449V.391H94.4v.007Zm0 4.255h-6.384V1.46h6.385v3.192ZM101.466 8.88V.391h1.079l3.415 3.451 2.912-3.451h1.079v8.487h-1.079V2.045l-2.373 2.877h-1.078l-2.876-2.877V8.88h-1.079Z"
    />
  </svg>
);

export default OnlyPlatformLetteringLogo;
