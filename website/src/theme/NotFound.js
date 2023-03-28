import React from "react";
import LetteringLogo from "@site/src/components/Icons/LetteringLogo";

export default function NotFound() {
  return (
    <div className="h-screen overflow-hidden">
      <div className="flex flex-col items-center justify-center mt-24 px-4">
        <LetteringLogo width={260} />
      </div>
      <div className="flex flex-col items-center justify-center h-[80%] px-4">
        <img
          // TODO - fix this Z-index
          alt="background"
          className="absolute -z-5 w-[1100px] h-[980px] object-cover"
          src="img/background404.png"
        />
        <div className="mt-20">
          <img
            src={
              // TODO - add 500 image and how to get status here
              status == 404
                ? "img/404.png"
                : "img/404.png"
            }
            width={612}
            height={271}
            alt="not found"
          />
          <div className="mt-8 flex-center flex-col gap-0">
            <h1 className="uppercase text-center tracking-widest font-bold text-2xl">
              OOPS! PAGE NOT FOUND!
            </h1>
            <p className="text-center text-xl mt-6">
              Sorry the page you’re looking for doesn’t exist.
              <br />
              If you think something is broken, please report a problem.
            </p>
            <div className="flex flex-col md:flex-row gap-6 mt-10 justify-center w-full">
            <a
                href="https://docs.openbb.co"
                target="_blank"
                rel="noopener noreferrer"
                className="_btn-secondary"
              >
                Return Home
              </a>
              <a
                // TODO - add link to report problem
                href="https://openbb.co/support"
                target="_blank"
                rel="noopener noreferrer"
                className="_btn-secondary"
              >
                Report problem
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
