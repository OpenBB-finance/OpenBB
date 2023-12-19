import React, { SVGProps } from "react";
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const OnlySDKLetteringLogo = ({
  title,
  titleId,
  ...props
}: SVGProps<SVGSVGElement> & SVGRProps) => (
  <svg
    width="39"
    height="9"
    viewBox="0 0 39 9"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M1.40966 1.4115H9.13987V0.15831H0.280029V5.70815H7.85463V7.67744H0.282374V9H9.13896V4.56424H1.40966V1.4115Z"
      fill="white"
    />
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M14.8998 0.15831V8.93063H21.7028L23.6721 6.78231V2.30663L21.7028 0.15831H14.8998ZM15.9739 7.85647V1.23247H20.9867L22.4189 2.78935V6.42426L20.9867 7.85647H15.9739Z"
      fill="white"
    />
    <path
      d="M30.506 0.15831H29.4319V8.93063H30.506V4.45496L36.593 8.93063H38.2042L31.5802 3.91788L36.0559 0.15831H34.6237L30.506 3.45505V0.15831Z"
      fill="white"
    />
  </svg>
);

export default OnlySDKLetteringLogo;
