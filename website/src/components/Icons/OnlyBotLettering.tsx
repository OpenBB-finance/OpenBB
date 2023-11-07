import React, { SVGProps } from "react";
interface SVGRProps {
  title?: string;
  titleId?: string;
}

const OnlyBotLetteringLogo: React.FC<SVGProps<SVGSVGElement> & SVGRProps> = ({
  title,
  titleId,
  ...props
}) => (
  <svg
    width="38"
    height="9"
    viewBox="0 0 38 9"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M28.9071 0.360001V1.44L32.7148 1.44V8.856H33.8238V1.44L37.6317 1.44V0.360001H33.8238H32.7148H28.9071Z"
      fill="white"
    />
    <path
      d="M21.9744 0.360001H14.859V9H22.9921V0.360001H21.9756H21.9744ZM21.9744 1.98041V7.92016H15.8743V1.43984H21.9744V1.98041Z"
      fill="white"
    />
    <path
      d="M7.83273 3.59952H6.724V0.360001H0.0716553V9H8.94409V3.59437H7.83537L7.83273 3.59952ZM1.18038 3.05638V1.43984H5.61528V3.59952H1.18038V3.05638ZM7.83273 5.21606V7.91888H1.18038V4.68064H7.83273V5.21606Z"
      fill="white"
    />
  </svg>
);

export default OnlyBotLetteringLogo;
